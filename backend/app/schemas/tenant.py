from datetime import datetime
from pydantic import BaseModel


class TenantCreate(BaseModel):
    name: str
    admin_email: str
    admin_password: str


class TenantResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True