import pandas as pd
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
    row_count=len(df)
    column_count=len(df.columns)
    logger.info(f"Count of records at source: {row_count}, total columns: {column_count}")

    print("\n===== DATA PREVIEW =====")
    print(df.head)

    print("\n===== SCHEMA =====")
    print(df.dtypes)

    logger.info("Current file ingested successfully")



