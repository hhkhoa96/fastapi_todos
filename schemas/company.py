from sqlalchemy import Column, String

from .base_entity import Base, BaseEntity


class Company(Base, BaseEntity):
    __tablename__ = "companies"

    name = Column(String, nullable=False)
