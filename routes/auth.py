from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

from database import get_session
from services.auth import sign_in, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    user = sign_in(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=404, detail="Incorrect username or password")

    token = create_access_token(user)

    return {
        "access_token": token,
        "token_type": "bearer"
    }
