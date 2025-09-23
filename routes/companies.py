from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from database import get_session
from schemas.company import Company

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("")
def get_companies(db: Session = Depends(get_session)):
    return db.query(Company).all()


@router.post("")
def add_company(name: str, description: str, rating: float,
                db: Session = Depends(get_session)):
    company = Company(name=name, description=description, rating=rating)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company
