from fastapi import APIRouter, Depends, HTTPException, status
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
async def get_users(current_user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_session)):
    if current_user['is_superuser']:
        return db.query(User).all()
    elif current_user['is_admin']:
        return db.query(User).filter(User.company_id == current_user["company_id"])
    else:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN)


# Can't create superuser account
@router.post("", response_model=ViewUser)
async def create_user(payload: UserCreate, current_user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_session)):
    if not current_user['is_admin']:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    company = (
        db.query(Company)
        .filter(Company.id == current_user['company_id'])
        .first()
    )

    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

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
        return new_admin
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    except Exception as e:
        logger(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.get("/{username}/tasks")
async def get_user_tasks_by_id(username: str, current_user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_session)):
    user = db.query(User).filter(User.username == username).first()
    if not current_user["is_admin"] or user.company_id is not current_user.company_id:
        raise HTTPException(401, "Permission denied")

    return user.tasks if user.tasks else []
