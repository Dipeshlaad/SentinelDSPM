from datetime import datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    alert_rule_id: int
    scan_id: int
    asset_id: int
    data_type: str
    threshold: int
    current_count: int
    severity: str
    title: str
    description: str | None
    status: str
    created_at: datetime
    resolved_at: datetime | None
    resolved_by_scan_id: int | None

    class Config:
        from_attributes = True