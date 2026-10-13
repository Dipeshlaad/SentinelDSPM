from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.policy import Policy
from app.schemas.policy import (
    PolicyResponse,
    PolicyStatusUpdate,
)
from app.core.permissions import require_permission
from app.core.security import get_current_user
from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/api/v1/policies",
    tags=["Policies"],
)


# ---------------------------------------------------------
# GET ALL POLICIES
# ---------------------------------------------------------
@router.get(
    "/",
    response_model=list[PolicyResponse],
)
def get_policies(
    current_user=Depends(
        require_permission("policy:read")
    ),
    db: Session = Depends(get_db),
):
    return (
        db.query(Policy)
        .order_by(Policy.id)
        .all()
    )


# ---------------------------------------------------------
# GET POLICY BY ID
# ---------------------------------------------------------
@router.get(
    "/{policy_id}",
    response_model=PolicyResponse,
)
def get_policy(
    policy_id: int,
    current_user=Depends(
        require_permission("policy:read")
    ),
    db: Session = Depends(get_db),
):
    policy = (
        db.query(Policy)
        .filter(Policy.id == policy_id)
        .first()
    )

    if policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found",
        )

    return policy


# ---------------------------------------------------------
# ENABLE / DISABLE POLICY
# ---------------------------------------------------------
@router.patch(
    "/{policy_id}/status",
    response_model=PolicyResponse,
)
def update_policy_status(
    policy_id: int,
    data: PolicyStatusUpdate,
    current_user=Depends(
        require_permission("policy:update")
    ),
    db: Session = Depends(get_db),
):
    policy = (
        db.query(Policy)
        .filter(Policy.id == policy_id)
        .first()
    )

    if policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found",
        )

    # Nothing changed
    if policy.is_active == data.is_active:
        return policy

    policy.is_active = data.is_active

    action = (
        "POLICY_ENABLED"
        if data.is_active
        else "POLICY_DISABLED"
    )

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action=action,
        resource_type="policy",
        resource_id=policy.id,
        details=(
            f"Policy {policy.name} was "
            f"{'enabled' if data.is_active else 'disabled'}"
        ),
    )

    db.commit()
    db.refresh(policy)

    return policy