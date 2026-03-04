import os
from datetime import timedelta

STORE_DATABASE_URL_KEY = "STORE_DATABASE_URL"
STORE_DATABASE_USERNAME_KEY = "STORE_DATABASE_USERNAME"
STORE_DATABASE_PASSWORD_KEY = "STORE_DATABASE_PASSWORD"
STORE_DATABASE_NAME_KEY = "STORE_DATABASE_NAME"

store_database_url = os.getenv(STORE_DATABASE_URL_KEY, "db_store:3306")
store_database_username = os.getenv(STORE_DATABASE_USERNAME_KEY, "root")
store_database_password = os.getenv(STORE_DATABASE_PASSWORD_KEY, "root")
store_database_name = os.getenv(STORE_DATABASE_NAME_KEY, "online_store")

class Config:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{store_database_username}:{store_database_password}@{store_database_url}/{store_database_name}"
    JWT_SECRET_KEY = "JWT_SECRET_DEV_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)