from datetime import timedelta
import os

AUTH_DATABASE_URL_KEY = "AUTH_DATABASE_URL"
AUTH_DATABASE_USERNAME_KEY = "AUTH_DATABASE_USERNAME"
AUTH_DATABASE_PASSWORD_KEY = "AUTH_DATABASE_PASSWORD"
AUTH_DATABASE_NAME_KEY = "AUTH_DATABASE_NAME"

auth_database_url = os.getenv(AUTH_DATABASE_URL_KEY, "localhost:3306")
auth_database_username = os.getenv(AUTH_DATABASE_USERNAME_KEY, "root")
auth_database_password = os.getenv(AUTH_DATABASE_PASSWORD_KEY, "root")
auth_database_name = os.getenv(AUTH_DATABASE_NAME_KEY, "online_store_auth")

class Config:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{auth_database_username}:{auth_database_password}@{auth_database_url}/{auth_database_name}"

    JWT_SECRET_KEY = "JWT_SECRET_DEV_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)