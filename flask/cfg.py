import logging
import os

logger = logging.getLogger("App")         
logger.setLevel(logging.INFO)
fh = logging.FileHandler("log.log")
formatter = logging.Formatter('%(asctime)s - %(name)s -'
                              ' %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


# Данные для базы PostgreSQL
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
