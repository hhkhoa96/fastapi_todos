from passlib.context import CryptContext

pw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pw_context.hash(password)