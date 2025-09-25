from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated

from database import get_session
from schemas.company import Company
from models.company import ViewCompany, CreateCompanyPayload
from schemas.user import User
from services.auth import get_current_user

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("", response_model=list[ViewCompany], status_code=status.HTTP_200_OK)
async def get_companies(current_user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_session)):
    return db.query(Company).all()


@router.post("", response_model=ViewCompany, status_code=status.HTTP_201_CREATED)
async def add_company(payload: CreateCompanyPayload, current_user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_session)):
    if not current_user['is_superuser']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    company = Company(**payload.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company
