from datetime import timedelta
import os

DATABASE_URL_KEY = "DATABASE_URL"
DATABASE_USERNAME_KEY = "DATABASE_USERNAME"
DATABASE_PASSWORD_KEY = "DATABASE_PASSWORD"
DATABASE_NAME_KEY = "DATABASE_NAME"

database_url = os.getenv(DATABASE_URL_KEY, "localhost:3306")
database_username = os.getenv(DATABASE_USERNAME_KEY, "root")
database_password = os.getenv(DATABASE_PASSWORD_KEY, "root")
database_name = os.getenv(DATABASE_NAME_KEY, "users")

class Configuration:
    SQLALCHEMY_DATABASE_URI   = f"mysql+pymysql://{database_username}:{database_password}@{database_url}/{database_name}"
    JWT_SECRET_KEY            = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta ( minutes = 15 )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta ( days = 30 )