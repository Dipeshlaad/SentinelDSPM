from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.alert_rule import AlertRule
from app.schemas.alert_rule import (
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertRuleResponse,
)
from app.core.permissions import require_permission
from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/api/v1/alert-rules",
    tags=["Alert Rules"]
)


SUPPORTED_DATA_TYPES = {
    "email",
    "phone",
    "aadhaar",
    "pan",
    "credit_card",
    "aws_access_key",
}


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post(
    "/",
    response_model=AlertRuleResponse
)
def create_alert_rule(
    rule_data: AlertRuleCreate,
    current_user=Depends(
        require_permission("policy:create")
    ),
    db: Session = Depends(get_db)
):
    if rule_data.data_type not in SUPPORTED_DATA_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported data type"
        )

    existing_rule = (
        db.query(AlertRule)
        .filter(
            AlertRule.data_type
            == rule_data.data_type,
            AlertRule.threshold
            == rule_data.threshold
        )
        .first()
    )

    if existing_rule is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                "An alert rule already exists for "
                "this data type and threshold"
            )
        )

    alert_rule = AlertRule(
        name=rule_data.name,
        data_type=rule_data.data_type,
        threshold=rule_data.threshold,
        is_active=True
    )

    db.add(alert_rule)
    db.flush()

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action="ALERT_RULE_CREATED",
        resource_type="alert_rule",
        resource_id=alert_rule.id,
        details=f"Alert rule {alert_rule.name} was created",
    )

    db.commit()
    db.refresh(alert_rule)

    return alert_rule


@router.get(
    "/",
    response_model=list[AlertRuleResponse]
)
def get_alert_rules(
    current_user=Depends(
        require_permission("policy:read")
    ),
    db: Session = Depends(get_db)
):
    return (
        db.query(AlertRule)
        .order_by(AlertRule.id)
        .all()
    )


@router.get(
    "/{rule_id}",
    response_model=AlertRuleResponse
)
def get_alert_rule(
    rule_id: int,
    current_user=Depends(
        require_permission("policy:read")
    ),
    db: Session = Depends(get_db)
):
    alert_rule = (
        db.query(AlertRule)
        .filter(
            AlertRule.id == rule_id
        )
        .first()
    )

    if alert_rule is None:
        raise HTTPException(
            status_code=404,
            detail="Alert rule not found"
        )

    return alert_rule


@router.put(
    "/{rule_id}",
    response_model=AlertRuleResponse
)
def update_alert_rule(
    rule_id: int,
    rule_data: AlertRuleUpdate,
    current_user=Depends(
        require_permission("policy:update")
    ),
    db: Session = Depends(get_db)
):
    alert_rule = (
        db.query(AlertRule)
        .filter(
            AlertRule.id == rule_id
        )
        .first()
    )

    if alert_rule is None:
        raise HTTPException(
            status_code=404,
            detail="Alert rule not found"
        )

    if rule_data.threshold is not None:

        duplicate_rule = (
            db.query(AlertRule)
            .filter(
                AlertRule.data_type
                == alert_rule.data_type,
                AlertRule.threshold
                == rule_data.threshold,
                AlertRule.id != alert_rule.id
            )
            .first()
        )

        if duplicate_rule is not None:
            raise HTTPException(
                status_code=409,
                detail=(
                    "An alert rule already exists for "
                    "this data type and threshold"
                )
            )

        alert_rule.threshold = rule_data.threshold

    if rule_data.name is not None:
        alert_rule.name = rule_data.name

    if rule_data.is_active is not None:
        alert_rule.is_active = rule_data.is_active

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action="ALERT_RULE_UPDATED",
        resource_type="alert_rule",
        resource_id=alert_rule.id,
        details=f"Alert rule {alert_rule.name} was updated",
    )

    db.commit()
    db.refresh(alert_rule)

    return alert_rule


@router.delete(
    "/{rule_id}"
)
def delete_alert_rule(
    rule_id: int,
    current_user=Depends(
        require_permission("policy:delete")
    ),
    db: Session = Depends(get_db)
):
    alert_rule = (
        db.query(AlertRule)
        .filter(
            AlertRule.id == rule_id
        )
        .first()
    )

    if alert_rule is None:
        raise HTTPException(
            status_code=404,
            detail="Alert rule not found"
        )

    deleted_rule_name = alert_rule.name

    db.delete(alert_rule)

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action="ALERT_RULE_DELETED",
        resource_type="alert_rule",
        resource_id=rule_id,
        details=f"Alert rule {deleted_rule_name} was deleted",
    )

    db.commit()

    return {
        "message": "Alert rule deleted successfully"
    }

