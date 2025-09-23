from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_session
from schemas.user import User
from schemas.company import Company
from models.user import ViewUser, UserCreate

router = APIRouter(prefix="/users", tags=["Users"])


# TODO: Should get list of users based on company the admin belongs to
@router.get("", response_model=list[ViewUser])
def get_users(db: Session = Depends(get_session)):
    return db.query(User).all()


@router.post("")
async def create_user(payload: UserCreate, db: Session = Depends(get_session)):
    try:
        company = (
            db.get_one(Company, payload.company_id)
            if payload.company_id else None
        )

        new_admin = User(
            username=payload.username,
            first_name=payload.first_name,
            last_name=payload.last_name,
            password=payload.password,
            is_admin=payload.is_admin,
            is_active=True,
            is_superuser=False,
            company_id=company.id
        )
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)

        return new_admin
    except Exception as e:

        return e
