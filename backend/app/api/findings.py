from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.database import SessionLocal
from app.models.finding import Finding
from app.models.asset import Asset
from app.models.datasource import Datasource
from app.schemas.finding import FindingResponse
from app.core.permissions import require_permission


router = APIRouter(
    prefix="/api/v1/findings",
    tags=["Findings"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get(
    "/",
    response_model=List[FindingResponse]
)
def get_findings(
    current_user=Depends(
        require_permission("finding:read")
    ),
    db=Depends(get_db)
):
    query = (
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

    # Tenant users can only see findings
    # belonging to their own tenant.
    if current_user["tenant_id"] is not None:
        query = query.filter(
            Datasource.tenant_id
            == current_user["tenant_id"]
        )

    return query.all()


@router.get(
    "/{finding_id}",
    response_model=FindingResponse
)
def get_finding(
    finding_id: int,
    current_user=Depends(
        require_permission("finding:read")
    ),
    db=Depends(get_db)
):
    finding = (
        db.query(Finding)
        .join(
            Asset,
            Finding.asset_id == Asset.id
        )
        .join(
            Datasource,
            Asset.datasource_id == Datasource.id
        )
        .filter(
            Finding.id == finding_id
        )
        .first()
    )

    # Finding does not exist at all.
    if finding is None:
        raise HTTPException(
            status_code=404,
            detail="Finding not found"
        )

    # System Admin can access findings
    # across all tenants.
    if current_user["tenant_id"] is None:
        return finding

    # Find the tenant that owns this finding.
    datasource = (
        db.query(Datasource)
        .join(
            Asset,
            Asset.datasource_id == Datasource.id
        )
        .filter(
            Asset.id == finding.asset_id
        )
        .first()
    )

    # Finding belongs to another tenant.
    if datasource.tenant_id != current_user["tenant_id"]:
        raise HTTPException(
            status_code=403,
            detail="You can only view findings of your tenant"
        )

    return finding