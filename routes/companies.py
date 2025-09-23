from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from database import get_session
from schemas.company import Company
from models.company import ViewCompany

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("", response_model=list[ViewCompany])
def get_companies(db: Session = Depends(get_session)):
    return db.query(Company).all()


@router.post("", response_model=ViewCompany)
def add_company(name: str, description: str, rating: float,
                db: Session = Depends(get_session)):
    company = Company(name=name, description=description, rating=rating)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company
