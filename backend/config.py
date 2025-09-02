import os

DB_USER = os.getenv("DB_USER", "danceuser")
DB_PASS = os.getenv("DB_PASS", "dancepass")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "dance_competition")

SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
