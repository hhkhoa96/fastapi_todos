from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Annotated

from database import get_session
from schemas.user import User
from schemas.company import Company
from models.user import ViewUser, UserCreate
from services.auth import hash_password, get_current_user
from services.logger import logger

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=list[ViewUser])
def get_users(current_user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_session)):
    if current_user['is_superuser']:
        return db.query(User).all()
    elif current_user['is_admin']:
        return db.query(User).filter(User.company_id == current_user["company_id"])
    else:
        return HTTPException(status_code=401)



@router.post("")
async def create_user(payload: UserCreate, db: Session = Depends(get_session)):
    company = (
        db.query(Company)
        .filter(Company.id == payload.company_id)
        .first()
    )

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    try:
        new_admin = User(
            username=payload.username,
            first_name=payload.first_name,
            last_name=payload.last_name,
            password=hash_password(payload.password),
            is_admin=payload.is_admin,
            is_active=True,
            is_superuser=False,
            company_id=company.id
        )
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
    except IntegrityError:  
        raise HTTPException(status_code=400, detail="Username already exists")
    except Exception as e:
        logger(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
