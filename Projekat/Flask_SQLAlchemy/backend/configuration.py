import os

DATABASE_URL = os.environ.get("DATABASE_URL", "localhost")

class Configuration:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{DATABASE_URL}/employees"