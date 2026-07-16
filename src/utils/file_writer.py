import os

def save_csv(df,path,file_name):
    os.makedirs(path,exist_ok=True)
    full_path=(f"{path}/{file_name}")
    df.to_csv(full_path,index=False)

    return full_path