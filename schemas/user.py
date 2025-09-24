from sqlalchemy import Column, String, Boolean, ForeignKey, UUID
from sqlalchemy.orm import relationship

from .base_entity import Base, BaseEntity


class User(Base, BaseEntity):
    __tablename__ = "users"

    username = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    company_id = Column(UUID(), ForeignKey("companies.id"))
    tasks = relationship("User")
