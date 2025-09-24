from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated


from database import get_session
from schemas.task import Task, Status
from models.task import CreateTaskPayload, ViewTask
from schemas.user import User
from services.auth import get_current_user
from services.logger import logger

router = APIRouter(prefix="/task", tags=["Task"])


@router.get("", response_model=list[ViewTask], status_code=status.HTTP_200_OK)
def get_tasks(current_user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_session)):
    logger(current_user)
    return db.query(Task).all()


@router.post("", response_model=ViewTask, status_code=status.HTTP_201_CREATED)
def create_task(payload: CreateTaskPayload, current_user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_session)):
    task = Task(**payload.model_dump())
    task.status = Status.TODO
    task.user_id = current_user['id']

    db.add(task)
    db.commit()
    db.refresh(task)
    return task
