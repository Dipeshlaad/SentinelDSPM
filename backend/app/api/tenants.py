from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantResponse
from app.core.permissions import require_permission
from app.models.user import User
from app.models.role import Role
from app.core.security import get_password_hash
from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/api/v1/tenants",
    tags=["Tenants"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# GET ALL TENANTS
@router.get(
    "/",
    response_model=List[TenantResponse]
)
def get_tenants(
    current_user=Depends(
        require_permission("tenant:read")
    ),
    db: Session = Depends(get_db)
):
    # System Admin can see all tenants
    if current_user["tenant_id"] is None:
        return db.query(Tenant).all()

    # Tenant Admin can only see their own tenant
    tenant = (
        db.query(Tenant)
        .filter(
            Tenant.id == current_user["tenant_id"]
        )
        .first()
    )

    if tenant is None:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found"
        )

    return [tenant]


# GET TENANT BY ID
@router.get(
    "/{tenant_id}",
    response_model=TenantResponse
)
def get_tenant(
    tenant_id: int,
    current_user=Depends(
        require_permission("tenant:read")
    ),
    db: Session = Depends(get_db)
):
    # Tenant Admin can only access their own tenant
    if current_user["tenant_id"] is not None:
        if tenant_id != current_user["tenant_id"]:
            raise HTTPException(
                status_code=404,
                detail="Tenant not found"
            )

    tenant = (
        db.query(Tenant)
        .filter(Tenant.id == tenant_id)
        .first()
    )

    if tenant is None:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found"
        )

    return tenant


# CREATE TENANT
@router.post(
    "/",
    response_model=TenantResponse
)
def create_tenant(
    tenant_data: TenantCreate,
    current_user=Depends(
        require_permission("tenant:create")
    ),
    db: Session = Depends(get_db)
):
    # Only System Admin can create tenants
    if current_user["tenant_id"] is not None:
        raise HTTPException(
            status_code=403,
            detail="Only System Admin can create tenants"
        )

    # Check whether tenant name already exists
    existing_tenant = (
        db.query(Tenant)
        .filter(Tenant.name == tenant_data.name)
        .first()
    )

    if existing_tenant is not None:
        raise HTTPException(
            status_code=409,
            detail="Tenant already exists"
        )

    # Check whether admin email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == tenant_data.admin_email)
        .first()
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=409,
            detail="Admin email already exists"
        )

    # Find TENANT_ADMIN role
    tenant_admin_role = (
        db.query(Role)
        .filter(Role.name == "TENANT_ADMIN")
        .first()
    )

    if tenant_admin_role is None:
        raise HTTPException(
            status_code=500,
            detail="TENANT_ADMIN role is not configured"
        )

    # Create tenant
    new_tenant = Tenant(
        name=tenant_data.name
    )

    db.add(new_tenant)
    db.flush()

    # Create Tenant Admin
    new_admin = User(
        email=tenant_data.admin_email,
        hashed_password=get_password_hash(
            tenant_data.admin_password
        ),
        tenant_id=new_tenant.id,
        role_id=tenant_admin_role.id
    )

    db.add(new_admin)

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=new_tenant.id,
        action="TENANT_CREATED",
        resource_type="tenant",
        resource_id=new_tenant.id,
        details=f"Tenant {new_tenant.name} was created",
    )

    db.commit()

    db.refresh(new_tenant)

    return new_tenant


# UPDATE TENANT
@router.put(
    "/{tenant_id}",
    response_model=TenantResponse
)
def update_tenant(
    tenant_id: int,
    tenant_data: TenantCreate,
    current_user=Depends(
        require_permission("tenant:update")
    ),
    db: Session = Depends(get_db)
):
    # Only System Admin can update tenants
    if current_user["tenant_id"] is not None:
        raise HTTPException(
            status_code=403,
            detail="Only System Admin can update tenants"
        )

    tenant = (
        db.query(Tenant)
        .filter(Tenant.id == tenant_id)
        .first()
    )

    if tenant is None:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found"
        )

    # Check duplicate tenant name
    existing_tenant = (
        db.query(Tenant)
        .filter(
            Tenant.name == tenant_data.name,
            Tenant.id != tenant_id
        )
        .first()
    )

    if existing_tenant is not None:
        raise HTTPException(
            status_code=409,
            detail="Tenant already exists"
        )

    tenant.name = tenant_data.name

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=tenant.id,
        action="TENANT_UPDATED",
        resource_type="tenant",
        resource_id=tenant.id,
        details=f"Tenant {tenant.name} was updated",
    )

    db.commit()

    db.refresh(tenant)

    return tenant


# DELETE TENANT
@router.delete(
    "/{tenant_id}"
)
def delete_tenant(
    tenant_id: int,
    current_user=Depends(
        require_permission("tenant:delete")
    ),
    db: Session = Depends(get_db)
):
    # Only System Admin can delete tenants
    if current_user["tenant_id"] is not None:
        raise HTTPException(
            status_code=403,
            detail="Only System Admin can delete tenants"
        )

    tenant = (
        db.query(Tenant)
        .filter(Tenant.id == tenant_id)
        .first()
    )

    if tenant is None:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found"
        )

    deleted_tenant_name = tenant.name

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action="TENANT_DELETED",
        resource_type="tenant",
        resource_id=tenant_id,
        details=f"Tenant {deleted_tenant_name} was deleted",
    )

    db.delete(tenant)

    db.commit()

    return {
        "message": "Tenant deleted successfully"
    }

