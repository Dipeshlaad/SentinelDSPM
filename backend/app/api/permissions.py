
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models.permission import Permission
from app.schemas.permission import PermissionResponse
from app.core.permissions import require_permission


router = APIRouter(
    prefix="/api/v1/permissions",
    tags=["Permissions"]
)


# Database dependency
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# Get all permissions
@router.get(
    "/",
    response_model=List[PermissionResponse]
)
def get_permissions(
    current_user=Depends(
        require_permission("tenant:read")
    ),
    db: Session = Depends(get_db)
):

    permissions = db.query(Permission).all()

    return permissions


# Get permission by ID
@router.get(
    "/{permission_id}",
    response_model=PermissionResponse
)
def get_permission(
    permission_id: int,
    current_user=Depends(
        require_permission("tenant:read")
    ),
    db: Session = Depends(get_db)
):

    permission = db.query(Permission).filter(
        Permission.id == permission_id
    ).first()

    if permission is None:
        raise HTTPException(
            status_code=404,
            detail="Permission not found"
        )

    return permission
