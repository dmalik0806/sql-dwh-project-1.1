import pandas as pd
import os
from utils.logger import get_logger
from utils.config import load_config
from utils.dq_checks import generate_dq_report
from utils.dq_checks import collect_error_records
from utils.metadata import get_file_metadata
from datetime import datetime
from utils.transformations import clean_claims_data
from utils.file_writer import save_csv
from utils.file_tracker import (
    load_processed_files,
    get_all_input_files,
    is_file_processed,
    mark_file_processed
)



logger=get_logger(__name__)

def ingest_claims():
    logger.info("Initiating Claims ingestion")
    start_time = datetime.now()
    config=load_config()
    input_path=config["input_path"]
    tracking_path=config["tracking_path"]
    processed_df = load_processed_files(tracking_path)
    files = get_all_input_files(input_path)
    for file in files:
        if is_file_processed(file,processed_df):
            logger.info(f"{file} already processed")
            continue
        file_path = os.path.join(input_path, file)

    logger.info(f"Reading file: {file_path}")

    #Capturing metadata of the input file
    metadata = get_file_metadata(file_path)
    audit_path=config["audit_path"]
    logger.info(f"Source File: {metadata['FileName']}")
    logger.info(f"File Size KB: {metadata['FileSizeKB']}")
    metadata_df = pd.DataFrame([metadata])
    metadata_df.to_csv(f"{audit_path}/metadata_report.csv",index=False)


    df=pd.read_csv(file_path)
    logger.info("CSV File loaded successfully")
    initial_count = len(df)
    # Added transformations.py to clean the csv file data
    df,rem_dup_count = clean_claims_data(df)
    logger.info(f"Duplicates removed: {rem_dup_count}")
    logger.info("Data Cleaning Updated")

    #Data Validation checks
    null_counts=df.isnull().sum()
    print(f"Total Null Counts in current file: {null_counts}")
    logger.info(f"Null Counts: {null_counts}")

    #Generate DQ report
    dq_report_df=generate_dq_report(df)
    logger.info(f"DQ Report generated successfully")

    #Generate error report
    error_report_df=collect_error_records(df)
    logger.info(f"Error Report generated successfully")

    output_path=config["processed_path"]
    output_file=save_csv(df,output_path,"claims_processed.csv")
    logger.info(f"Processed file {output_file} saved at {output_path}")

    #Storing DQ report in csv
    dq_output_file=save_csv(dq_report_df,output_path,"dq_report.csv")
    logger.info(f"DQ Report saved at: {dq_output_file}")

    #Storing error records in csv
    error_output_path=config["error_path"]
    error_output_file=save_csv(error_report_df,error_output_path,"error_records.csv")
    logger.info(f"Error file {error_output_file} saved at {error_output_path} with {len(error_report_df)} records")

    end_time = datetime.now()
    runtime_seconds = (end_time - start_time).total_seconds()
    logger.info(f"Pipeline Runtime: {runtime_seconds}")

    summary_df = pd.DataFrame([
    {
        "SourceFile": metadata["FileName"],
        "InputRows": initial_count,
        "ProcessedRows": len(df),
        "ErrorRows": len(error_report_df),
        "RuntimeSeconds": runtime_seconds
    }
    ])

    summary_df.to_csv(f"{audit_path}/processing_summary.csv",index=False)

    logger.info(
        f"""
        Source File      : {metadata['FileName']}
        Input Rows       : {initial_count}
        Processed Rows   : {len(df)}
        Error Rows       : {len(error_report_df)}
        Runtime Seconds  : {runtime_seconds}
        """
    )






