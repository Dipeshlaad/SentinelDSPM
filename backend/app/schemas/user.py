from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str
    tenant_id: int | None = None
    role_id: int


class UserResponse(BaseModel):
    id: int
    email: str
    tenant_id: int | None
    role_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserUpdate(BaseModel):
    email: str | None = None
    password: str | None = None
    tenant_id: int | None = None
    role_id: int | None = None

