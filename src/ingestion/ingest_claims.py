import pandas as pd
import os
from utils.logger import get_logger
from utils.config import load_config

logger=get_logger(__name__)

def ingest_claims():
    logger.info("Initiating Claims ingestion")

    config=load_config()
    input_path=config["input_path"]
    file_path=f"{input_path}/claims_data.csv"
    logger.info(f"Reading file: {file_path}")

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

    output_path=config["processed_path"]
    os.makedirs(output_path, exist_ok=True)
    output_file=f"{output_path}/claims_processed.csv"
    df.to_csv(output_file,index=False)
    logger.info(f"Processed file {output_file} saved at {output_path}")




