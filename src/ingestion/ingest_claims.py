import pandas as pd
import os
from utils.logger import get_logger
from utils.config import load_config
from utils.dq_checks import generate_dq_report
from utils.dq_checks import collect_error_records
from utils.metadata import get_file_metadata
from datetime import datetime



logger=get_logger(__name__)

def ingest_claims():
    logger.info("Initiating Claims ingestion")
    start_time = datetime.now()
    config=load_config()
    input_path=config["input_path"]
    file_path=f"{input_path}/claims_data.csv"
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
    initial_count=len(df)
    df=df.drop_duplicates()
    rem_dup_count=len(df)
    logger.info(f"Duplicates removed: {initial_count-rem_dup_count}")

    #stripping whitespace from string columns
    string_columns=['PatientID','ProviderID','DiagnosisCode']
    for col in string_columns:
        df[col] = df[col].astype(str).str.strip()

    # updating data types
    df["DateOfService"] = pd.to_datetime(df["DateOfService"],format="%d-%m-%Y")
    df["ClaimedAmount"] = pd.to_numeric(df["ClaimedAmount"])
    df["ApprovedAmount"] = pd.to_numeric(df["ApprovedAmount"])
    
    #handling missing values
    df["DiagnosisCode"]=df["DiagnosisCode"].replace("nan", pd.NA).fillna("NA")
    df["ClaimedAmount"]=df["ClaimedAmount"].fillna(0)
    df["ApprovedAmount"]=df["ApprovedAmount"].fillna(0)
    df["DateOfService"]=df["DateOfService"].fillna(pd.Timestamp("1900-01-01"))

    logger.info("Data Cleaning Updated")

    #Data Validation checks
    null_counts=df.isnull().sum()
    print(f"Total Null Counts in current file: {null_counts}")
    logger.info(f"Null Counts: {null_counts}")

    negative_claims=df[df["ClaimedAmount"]<0]
    logger.info(f"Total count of invalid claims: {len(negative_claims)}")

    invalid_amount_rec = df[df["ApprovedAmount"]>df["ClaimedAmount"]]
    logger.info(f"Total count of Invalid Approvals: {len(invalid_amount_rec)}")

    #Generate DQ report
    dq_report_df=generate_dq_report(df)
    logger.info(f"DQ Report generated successfully")

    #Generate error report
    error_report_df=collect_error_records(df)
    logger.info(f"Error Report generated successfully")

    output_path=config["processed_path"]
    os.makedirs(output_path, exist_ok=True)
    output_file=f"{output_path}/claims_processed.csv"
    df.to_csv(output_file,index=False)
    logger.info(f"Processed file {output_file} saved at {output_path}")

    #Storing DQ report in csv
    dq_output_file=f"{output_path}/dq_report.csv"
    dq_report_df.to_csv(dq_output_file,index=False)
    logger.info(f"DQ Report saved at: {dq_output_file}")

    #Storing error records in csv
    error_output_path=config["error_path"]
    os.makedirs(error_output_path, exist_ok=True)
    error_output_file=f"{error_output_path}/error_records.csv"
    error_report_df.to_csv(error_output_file,index=False)
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






