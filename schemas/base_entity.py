from sqlalchemy import Column, UUID, Time
import uuid
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BaseEntity:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(Time, nullable=False, default="now()")
    updated_at = Column(Time, nullable=False, default="now()", onupdate="now()")
