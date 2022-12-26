import os
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv(verbose=True)


class DatabaseSetting:
    DB_USER_NAME = os.getenv("DB_USER_NAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER_NAME}:{quote(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


database_setting = DatabaseSetting()
