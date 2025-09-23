from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import db_engine, db_username, db_password, db_host, db_port, db_table


connection_str = f"{db_engine}://{db_username}:{db_password}@{db_host}:{db_port}/{db_table}"


engine = create_engine(connection_str, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
