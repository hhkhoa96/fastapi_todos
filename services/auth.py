from typing import Optional
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from jose import jwt

from schemas.user import User
from settings import jwt_secret, jwt_algorithm

pw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def hash_password(password: str) -> str:
    return pw_context.hash(password)

def verfiy_password(plain_password: str, hashed_password: str):
    return pw_context.verify(secret=plain_password, hash=hashed_password)


def sign_in(username: str, password: str, db: Session):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return None
    
    return user if verfiy_password(password, user.password) else None


def create_access_token(user: User):
    claims = {
        "sub": user.username,
        "id": str(user.id),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_admin": user.is_admin,
        "company_id": str(user.company_id),
        # "exp": datetime.now(timedelta(minutes=5))
    }
    return jwt.encode(claims, jwt_secret, algorithm=jwt_algorithm)
