from datetime import datetime

from pydantic import BaseModel, Field


class AlertRuleCreate(BaseModel):
    name: str
    data_type: str
    threshold: int = Field(gt=0)


class AlertRuleUpdate(BaseModel):
    name: str | None = None
    threshold: int | None = Field(
        default=None,
        gt=0
    )
    is_active: bool | None = None


class AlertRuleResponse(BaseModel):
    id: int
    name: str
    data_type: str
    threshold: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

