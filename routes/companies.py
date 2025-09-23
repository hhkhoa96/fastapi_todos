from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session


from database import get_session
from schemas.company import Company
from models.company import ViewCompany, CreateCompanyPayload

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("", response_model=list[ViewCompany], status_code=status.HTTP_200_OK)
def get_companies(db: Session = Depends(get_session)):
    return db.query(Company).all()


@router.post("", response_model=ViewCompany, status_code=status.HTTP_201_CREATED)
def add_company(payload: CreateCompanyPayload, db: Session = Depends(get_session)):
    company = Company(**payload.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company
