from datetime import datetime

from pydantic import BaseModel

class ScanCreate(BaseModel):
    name: str
    datasource_id: int

class ScanChangeResponse(BaseModel):
    change_type: str
    asset_id: int
    asset_name: str
    asset_path: str
    data_type: str | None
    previous_count: int | None
    current_count: int | None
    change: int | None
    status: str

class ScanSummaryResponse(BaseModel):
    total_assets: int
    assets_with_findings: int
    total_detections: int
    resolved_findings: int
    increased_findings: int
    decreased_findings: int
    unchanged_findings: int
    alerts_created: int

class ScanResponse(BaseModel):
    id: int
    name: str
    datasource_id: int
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime


    changes: list[ScanChangeResponse] = []
    summary: ScanSummaryResponse | None = None

    class Config:
        from_attributes = True

