import os
from datetime import datetime

def get_file_metadata(file_path):
    file_stats=os.stat(file_path)

    return {
        "FileName": os.path.basename(file_path),
        "FileSizeKB": round(file_stats.st_size / 1024, 2),
        "CreatedTime": datetime.fromtimestamp(file_stats.st_birthtime),
        "ModifiedTime": datetime.fromtimestamp(file_stats.st_mtime)
    }
