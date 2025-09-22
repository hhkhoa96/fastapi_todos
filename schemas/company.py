from sqlalchemy import Column, String, Integer, CheckConstraint

from .base_entity import Base, BaseEntity


class Company(Base, BaseEntity):
    __tablename__ = "companies"

    name = Column(String, nullable=False)
    description = Column(String)
    rating = Column(
        Integer,
        CheckConstraint("value BETWEEN 1 AND 5"),
        nullable=False
    )
