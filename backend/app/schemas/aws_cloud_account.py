from datetime import datetime

from pydantic import BaseModel, Field


class AWSCloudAccountCreate(BaseModel):

    name: str
    account_id: str = Field(
        pattern=r"^\d{12}$"
    )
    account_name: str

    role_name: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9+=,.@_-]+$"
    )

    region: str = Field(
    pattern=r"^[a-z]{2}-[a-z]+-\d+$"
    )


class AWSCloudAccountResponse(BaseModel):

    id: int
    tenant_id: int
    name: str
    account_id: str
    account_name: str
    role_name: str
    external_id: str
    region: str
    status: str
    last_verified_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True