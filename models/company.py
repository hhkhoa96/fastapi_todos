from pydantic import BaseModel, UUID4


class ViewCompany(BaseModel):
    id: UUID4
    name: str
    description: str
    rating: float
