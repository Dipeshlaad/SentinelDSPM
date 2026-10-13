from datetime import datetime

from pydantic import BaseModel


class FindingResponse(BaseModel):
    id: int
    asset_id: int
    data_type: str
    count: int
    severity: str
    created_at: datetime
    last_seen_at: datetime

    class Config:
        from_attributes = True