from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.schemas.bootstrap import SystemAdminBootstrap
from app.core.security import get_password_hash


router = APIRouter(
    prefix="/api/v1/bootstrap",
    tags=["Bootstrap"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def bootstrap_system(
    data: SystemAdminBootstrap,
    db: Session = Depends(get_db)
):
    system_admin_role = (
        db.query(Role)
        .filter(Role.name == "SYSTEM_ADMIN")
        .first()
    )

    if system_admin_role is None:
        raise HTTPException(
            status_code=500,
            detail="SYSTEM_ADMIN role is not configured"
        )

    existing_system_admin = (
        db.query(User)
        .filter(User.role_id == system_admin_role.id)
        .first()
    )

    if existing_system_admin is not None:
        raise HTTPException(
            status_code=403,
            detail="System is already initialized"
        )

    existing_email = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if existing_email is not None:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered"
        )

    new_system_admin = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        tenant_id=None,
        role_id=system_admin_role.id
    )

    db.add(new_system_admin)
    db.commit()
    db.refresh(new_system_admin)

    return {
        "message": "System Admin created successfully",
        "id": new_system_admin.id,
        "email": new_system_admin.email
    }