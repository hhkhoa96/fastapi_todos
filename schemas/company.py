from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from .base_entity import Base, BaseEntity


class Company(Base, BaseEntity):
    __tablename__ = "companies"

    name = Column(String, nullable=False)
    description = Column(String)
    rating = Column(Integer, nullable=False)

    users = relationship("User")
