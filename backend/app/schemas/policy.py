from datetime import datetime

from pydantic import BaseModel


class PolicyResponse(BaseModel):
    id: int
    name: str
    description: str | None
    data_type: str
    severity: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PolicyStatusUpdate(BaseModel):
    is_active: bool