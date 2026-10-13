from fastapi import APIRouter, Depends

from app.core.permissions import require_permission
from app.models.asset import Asset
from app.models.datasource import Datasource
from app.models.finding import Finding
from app.models.scan import Scan
from app.services.risk import calculate_asset_risk_level


router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Dashboard"]
)


def get_db():
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/summary")
def get_dashboard_summary(
    current_user=Depends(
        require_permission("datasource:read")
    ),
    db=Depends(get_db)
):
    asset_query = (
        db.query(Asset)
        .join(
            Datasource,
            Asset.datasource_id == Datasource.id
        )
    )

    finding_query = (
        db.query(Finding)
        .join(
            Asset,
            Finding.asset_id == Asset.id
        )
        .join(
            Datasource,
            Asset.datasource_id == Datasource.id
        )
    )

    datasource_query = db.query(Datasource)

    scan_query = (
        db.query(Scan)
        .join(
            Datasource,
            Scan.datasource_id == Datasource.id
        )
    )

    if current_user["tenant_id"] is not None:
        tenant_id = current_user["tenant_id"]

        asset_query = asset_query.filter(
            Datasource.tenant_id == tenant_id
        )

        finding_query = finding_query.filter(
            Datasource.tenant_id == tenant_id
        )

        datasource_query = datasource_query.filter(
            Datasource.tenant_id == tenant_id
        )

        scan_query = scan_query.filter(
            Datasource.tenant_id == tenant_id
        )

    assets = asset_query.all()

    total_assets = len(assets)
    total_findings = finding_query.count()
    total_datasources = datasource_query.count()
    total_scans = scan_query.count()

    risk_summary = {
        "none": 0,
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0
    }

    for asset in assets:
        risk = calculate_asset_risk_level(
            db,
            asset.id
        )

        risk_summary[risk["level"]] += 1

    return {
        "total_assets": total_assets,
        "total_findings": total_findings,
        "risk_summary": risk_summary,
        "total_datasources": total_datasources,
        "total_scans": total_scans
    }