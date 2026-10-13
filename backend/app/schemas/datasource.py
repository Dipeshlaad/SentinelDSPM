from datetime import datetime

from pydantic import BaseModel


class DatasourceCreate(BaseModel):

    name: str
    type: str
    tenant_id: int
    aws_cloud_account_id: int | None = None
    status: str = "active"


class DatasourceResponse(BaseModel):

    id: int
    name: str
    type: str
    tenant_id: int
    aws_cloud_account_id: int | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True