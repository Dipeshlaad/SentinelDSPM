from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.database import SessionLocal
from app.models.asset import Asset
from app.models.datasource import Datasource
from app.schemas.asset import AssetResponse
from app.core.permissions import require_permission
from app.services.risk import calculate_asset_risk_level

VALID_RISK_LEVELS = {
    "none",
    "low",
    "medium",
    "high",
    "critical"
}


router = APIRouter(
    prefix="/api/v1/assets",
    tags=["Assets"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get(
    "/",
    response_model=List[AssetResponse]
)
def get_assets(
    risk_level: str | None = None,
    current_user=Depends(
        require_permission("datasource:read")
    ),
    db=Depends(get_db)
):
    if (
        risk_level is not None
        and risk_level.lower() not in VALID_RISK_LEVELS
    ):
        raise HTTPException(
            status_code=400,
            detail="Please give a valid risk level[None,Low,Medium,High,Critical]"
        )
    
    query = (
        db.query(Asset)
        .join(
            Datasource,
            Asset.datasource_id == Datasource.id
        )
    )

    if current_user["tenant_id"] is not None:
        query = query.filter(
            Datasource.tenant_id
            == current_user["tenant_id"]
        )

    assets = query.all()

    results = []

    for asset in assets:
        risk = calculate_asset_risk_level(
            db,
            asset.id
        )

        if (
            risk_level is not None
            and risk["level"] != risk_level.lower()
        ):
            continue


        results.append(
            {
                "id": asset.id,
                "name": asset.name,
                "type": asset.type,
                "path": asset.path,
                "size": asset.size,
                "datasource_id": asset.datasource_id,
                "created_at": asset.created_at,
                "last_scanned_at": asset.last_scanned_at,
                "risk_score": risk["score"],
                "risk_level": risk["level"]
            }
        )

    return results

@router.get("/risk-summary")
def get_risk_summary(
    current_user=Depends(
        require_permission("datasource:read")
    ),
    db=Depends(get_db)
):
    query = (
        db.query(Asset)
        .join(
            Datasource,
            Asset.datasource_id == Datasource.id
        )
    )

    if current_user["tenant_id"] is not None:
        query = query.filter(
            Datasource.tenant_id
            == current_user["tenant_id"]
        )

    assets = query.all()

    summary = {
        "none": 0,
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
        "total": 0
    }

    for asset in assets:
        risk = calculate_asset_risk_level(
            db,
            asset.id
        )

        summary[risk["level"]] += 1
        summary["total"] += 1

    return summary

@router.get(
    "/{asset_id}",
    response_model=AssetResponse
)
def get_asset(
    asset_id: int,
    current_user=Depends(
        require_permission("datasource:read")
    ),
    db=Depends(get_db)
):
    query = (
        db.query(Asset)
        .join(
            Datasource,
            Asset.datasource_id == Datasource.id
        )
        .filter(
            Asset.id == asset_id
        )
    )

    if current_user["tenant_id"] is not None:
        query = query.filter(
            Datasource.tenant_id
            == current_user["tenant_id"]
        )

    asset = query.first()

    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )

    risk = calculate_asset_risk_level(
    db,
    asset.id
    )

    return {
        "id": asset.id,
        "name": asset.name,
        "type": asset.type,
        "path": asset.path,
        "size": asset.size,
        "datasource_id": asset.datasource_id,
        "created_at": asset.created_at,
        "last_scanned_at": asset.last_scanned_at,
        "risk_score": risk["score"],
        "risk_level": risk["level"]
    }

