import pandas as pd

#file_path=f"D:/Dhruv Malik/Projects/sql-dwh-project-1.1/data/raw/claims_data.csv"
#df=pd.read_csv(file_path)

def generate_dq_report(df):
    dq_results = []
    for col in df.columns:
        null_count = df[col].isnull().sum()
        duplicate_count = df[col].duplicated().sum()
        data_type = str(df[col].dtype)

        dq_results.append({
            "ColumnName":col,
            "NullCount":null_count,
            "DuplicateCount":duplicate_count,
            "DataType":data_type
        })
    
    dq_report_df=pd.DataFrame(dq_results)
    return dq_report_df

def collect_error_records(df):
    error_frames=[]
    #Rule1: negative claims
    negative_claims=df[df["ClaimedAmount"] < 0].copy()

    if not negative_claims.empty:
        negative_claims["ErrorReason"] = "Negative Claim Amount"
        error_frames.append(negative_claims)

    #Rule2: Invalid Claims i.e. Approved Amount > Claimed Amount
    invalid_claims=df[df["ApprovedAmount"]>df["ClaimedAmount"]].copy()

    if not invalid_claims.empty:
        invalid_claims["ErrorReason"] = "Approved Amount greater than Claimed Amount"
        error_frames.append(invalid_claims)

    #Rule3
    missing_diagnosis=df[df["DiagnosisCode"] == "NA"]

    if not missing_diagnosis.empty:
        missing_diagnosis["ErrorReason"] = "Missing Diagnosis Code"
        error_frames.append(missing_diagnosis)

    if error_frames:
        return pd.concat(error_frames)
    
    return pd.DataFrame()


        


