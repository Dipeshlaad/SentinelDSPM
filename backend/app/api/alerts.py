from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.alert import Alert
from app.models.asset import Asset
from app.models.datasource import Datasource
from app.schemas.alert import AlertResponse
from app.core.permissions import require_permission
from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/api/v1/alerts",
    tags=["Alerts"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/",
    response_model=list[AlertResponse]
)
def get_alerts(
    current_user=Depends(
        require_permission("policy:read")
    ),
    db: Session = Depends(get_db)
):
    query = (
        db.query(Alert)
        .join(
            Asset,
            Alert.asset_id == Asset.id
        )
        .join(
            Datasource,
            Asset.datasource_id == Datasource.id
        )
        .order_by(
            Alert.created_at.desc()
        )
    )

    # Tenant users can only see alerts
    # belonging to their own tenant.
    if current_user["tenant_id"] is not None:
        query = query.filter(
            Datasource.tenant_id
            == current_user["tenant_id"]
        )

    return query.all()


@router.get(
    "/{alert_id}",
    response_model=AlertResponse
)
def get_alert(
    alert_id: int,
    current_user=Depends(
        require_permission("policy:read")
    ),
    db: Session = Depends(get_db)
):
    query = (
        db.query(Alert)
        .join(
            Asset,
            Alert.asset_id == Asset.id
        )
        .join(
            Datasource,
            Asset.datasource_id == Datasource.id
        )
        .filter(
            Alert.id == alert_id
        )
    )

    # Tenant users can only access alerts
    # belonging to their own tenant.
    if current_user["tenant_id"] is not None:
        query = query.filter(
            Datasource.tenant_id
            == current_user["tenant_id"]
        )

    alert = query.first()

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    return alert


@router.patch(
    "/{alert_id}/status",
    response_model=AlertResponse
)
def update_alert_status(
    alert_id: int,
    status: str,
    current_user=Depends(
        require_permission("policy:update")
    ),
    db: Session = Depends(get_db)
):
    allowed_statuses = {
        "OPEN",
        "ACKNOWLEDGED",
        "RESOLVED"
    }

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid alert status"
        )

    query = (
        db.query(Alert)
        .join(
            Asset,
            Alert.asset_id == Asset.id
        )
        .join(
            Datasource,
            Asset.datasource_id == Datasource.id
        )
        .filter(
            Alert.id == alert_id
        )
    )

    # Tenant users can only modify alerts
    # belonging to their own tenant.
    if current_user["tenant_id"] is not None:
        query = query.filter(
            Datasource.tenant_id
            == current_user["tenant_id"]
        )

    alert = query.first()

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    old_status = alert.status

    if old_status == status:
        return alert

    alert.status = status

    action_map = {
        "ACKNOWLEDGED": "ALERT_ACKNOWLEDGED",
        "RESOLVED": "ALERT_RESOLVED",
        "OPEN": "ALERT_REOPENED",
    }

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action=action_map[status],
        resource_type="alert",
        resource_id=alert.id,
        details=(
            f"Alert {alert.title} status changed "
            f"from {old_status} to {status}"
        ),
    )

    db.commit()
    db.refresh(alert)

    return alert

