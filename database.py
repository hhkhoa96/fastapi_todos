from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os


load_dotenv()


def get_connection_str():
    db_engine = os.getenv("DB_ENGINE")
    db_username = os.getenv("DB_USERNAME")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_table = os.getenv("DB_TABLE")

    return f"{db_engine}://{db_username}:{db_password}@{db_host}:{db_port}/{db_table}"


engine = create_engine(get_connection_str(), echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
