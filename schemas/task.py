from sqlalchemy import Column, String, Boolean, ForeignKey, UUID, Integer

from .base_entity import Base, BaseEntity


class Task(Base, BaseEntity):
    __tablename__ = "tasks"

    summary = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    status = Column(Boolean, nullable=False)
    priority = Column(Integer, nullable=False)

    user_id = Column(UUID(), ForeignKey("users.id"))
