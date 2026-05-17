import logging
from datetime import datetime
import os

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

log_filename = f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_logger(name):
    return logging.getLogger(name)