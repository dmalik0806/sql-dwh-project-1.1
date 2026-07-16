import pandas as pd

def clean_claims_data(df):
    initial_count=len(df)
    df=df.drop_duplicates()
    rem_dup_count=initial_count - len(df)
    #Removing empty spaces for string type columns
    string_columns = ["PatientID","ProviderID","DiagnosisCode"]

    for col in string_columns:
        df[col]=(df[col].astype(str).str.strip())
    #Updating the data type for numeric columns
    int_columns = ["ClaimedAmount","ApprovedAmount"]

    for col in int_columns:
        df[col] = pd.to_numeric(df[col])
        df[col] = df[col].fillna(0)
    
    df["DiagnosisCode"] = (df["DiagnosisCode"].replace("nan",pd.NA).fillna("NA"))
    df["DateOfService"] = pd.to_datetime(df["DateOfService"],format="%d-%m-%Y")
    df["DateOfService"] = df["DateOfService"].fillna(pd.Timestamp("1900-01-01"))

    return df, rem_dup_count