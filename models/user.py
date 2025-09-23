
from pydantic import UUID4, BaseModel


class ViewUser(BaseModel):
    id: UUID4
    username: str
    is_active: bool
    is_admin: bool
    is_superuser: bool
    company_id: UUID4 | None


class UserCreate(BaseModel):
    username: str
    first_name: str
    last_name: str
    password: str
    is_admin: bool = False
    company_id: UUID4 | None = None
