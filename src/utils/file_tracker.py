import os
import pandas as pd
from datetime import datetime

def load_processed_files(metadata_path):
    file_path = os.path.join(metadata_path,"processed_files.csv")

    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    
    return pd.DataFrame(columns=["FileName","ProcessedTimestamp","Status"])

def get_all_input_files(input_path):
    files=[]
    for file in os.listdir(input_path):
        if file.endswith(".csv"):
            files.append(file)
    return files

def is_file_processed(file_name,processed_df):
    
    matching_rows = processed_df[
        (processed_df["FileName"] == file_name)
        &
        (processed_df["Status"] == "SUCCESS")
    ]

    if matching_rows.empty:
        return False
    
    return True

def mark_file_processed(processed_df,metadata_path,file_name,status):
    new_record = pd.DataFrame(
        [
            {
                "FileName":file_name,
                "ProcessedTimestamp":datetime.now(),
                "Status":status

            }
        ]
    )

    processed_df = pd.concat([processed_df, new_record], ignore_index=True)
    file_path = os.path.join(metadata_path,"processed_files.csv")
    processed_df.to_csv(file_path,index=False)

    return processed_df





