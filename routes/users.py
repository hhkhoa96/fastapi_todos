from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_session
from schemas.user import User
from schemas.company import Company
from models.user import ViewUser, UserCreate
from services.auth import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


# TODO: Should get list of users based on company the admin belongs to
@router.get("", response_model=list[ViewUser])
def get_users(db: Session = Depends(get_session)):
    return db.query(User).all()


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
        print("============== LOG ERROR ==================")
        print(e)
        print("============ END LOG ERROR ================")
        raise HTTPException(status_code=500, detail="Internal Server Error")
