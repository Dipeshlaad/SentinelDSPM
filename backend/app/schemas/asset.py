from datetime import datetime

from pydantic import BaseModel


class AssetResponse(BaseModel):
    id: int
    name: str
    type: str
    path: str
    size: int | None
    datasource_id: int
    created_at: datetime
    last_scanned_at: datetime | None
    risk_score: int
    risk_level: str

    class Config:
        from_attributes = True