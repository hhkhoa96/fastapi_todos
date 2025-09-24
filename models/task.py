from typing import Optional
from pydantic import BaseModel, UUID4, Field

from schemas.task import Status


class ViewTask(BaseModel):
    summary: str
    description: str
    priority: int
    status: Status
    user_id: UUID4

class CreateTaskPayload(BaseModel):
    summary: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(max_length=256)
    priority: int = Field(ge=0)
