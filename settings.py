from dotenv import load_dotenv
import os


load_dotenv()


db_engine = os.getenv("DB_ENGINE")
db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_table = os.getenv("DB_TABLE")

jwt_secret = os.getenv("JWT_SECRET")
jwt_algorithm = os.getenv("JWT_ALGORITHM")