from sqlalchemy import Column, String, Boolean, ForeignKey, UUID, Integer, Enum
import enum

from .base_entity import Base, BaseEntity

class Status(enum.Enum):
    TODO = 1
    IN_PROGRESS = 2
    COMPLETED = 3
    REMOVED = 4


class Task(Base, BaseEntity):
    __tablename__ = "task"

    summary = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    status = Column(Enum(Status), nullable=False)
    priority = Column(Integer, nullable=False)

    user_id = Column(UUID(), ForeignKey("users.id"))
