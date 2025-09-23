from pydantic import BaseModel, UUID4, Field


class ViewCompany(BaseModel):
    id: UUID4
    name: str
    description: str
    rating: float


class CreateCompanyPayload(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=256)
    rating: int = Field(ge=1, le=5)
