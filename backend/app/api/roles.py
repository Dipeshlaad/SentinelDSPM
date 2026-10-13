from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleResponse
from app.core.permissions import require_permission
from app.core.security import get_current_user
from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/api/v1/roles",
    tags=["Roles"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# Get all roles
# Any signed-in user may list roles (tenant admins need this to create users).
# Tenant-level users never see the SYSTEM_ADMIN role.
@router.get(
    "/",
    response_model=List[RoleResponse]
)
def get_roles(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Role)

    if current_user["tenant_id"] is not None:
        query = query.filter(Role.name != "SYSTEM_ADMIN")

    return query.all()


# Get role by ID
@router.get(
    "/{role_id}",
    response_model=RoleResponse
)
def get_role(
    role_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    role = db.query(Role).filter(
        Role.id == role_id
    ).first()

    if role is None:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )

    if (
        current_user["tenant_id"] is not None
        and role.name == "SYSTEM_ADMIN"
        and role.id != current_user["role_id"]
    ):
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )

    return role


# Create role
@router.post(
    "/",
    response_model=RoleResponse
)
def create_role(
    role_data: RoleCreate,
    current_user=Depends(
        require_permission("tenant:create")
    ),
    db: Session = Depends(get_db)
):

    # Only System Admin should be able to create roles.
    if current_user["tenant_id"] is not None:
        raise HTTPException(
            status_code=403,
            detail="Only System Admin can create roles"
        )

    # Prevent duplicate role names
    existing_role = db.query(Role).filter(
        Role.name == role_data.name
    ).first()

    if existing_role is not None:
        raise HTTPException(
            status_code=400,
            detail="Role already exists"
        )

    new_role = Role(
        name=role_data.name
    )

    db.add(new_role)
    db.flush()

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action="ROLE_CREATED",
        resource_type="role",
        resource_id=new_role.id,
        details=f"Role {new_role.name} was created",
    )

    db.commit()

    db.refresh(new_role)

    return new_role


# Update role
@router.put(
    "/{role_id}",
    response_model=RoleResponse
)
def update_role(
    role_id: int,
    role_data: RoleCreate,
    current_user=Depends(
        require_permission("tenant:update")
    ),
    db: Session = Depends(get_db)
):

    # Only System Admin can modify roles
    if current_user["tenant_id"] is not None:
        raise HTTPException(
            status_code=403,
            detail="Only System Admin can update roles"
        )

    role = db.query(Role).filter(
        Role.id == role_id
    ).first()

    if role is None:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )

    # Protect built-in system roles
    if role.name in ["SYSTEM_ADMIN", "TENANT_ADMIN"]:
        raise HTTPException(
            status_code=400,
            detail="System roles cannot be modified"
        )

    # Prevent duplicate role names
    existing_role = db.query(Role).filter(
        Role.name == role_data.name,
        Role.id != role_id
    ).first()

    if existing_role is not None:
        raise HTTPException(
            status_code=400,
            detail="Role already exists"
        )

    role.name = role_data.name

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action="ROLE_UPDATED",
        resource_type="role",
        resource_id=role.id,
        details=f"Role {role.name} was updated",
    )

    db.commit()

    db.refresh(role)

    return role


# Delete role
@router.delete(
    "/{role_id}"
)
def delete_role(
    role_id: int,
    current_user=Depends(
        require_permission("tenant:delete")
    ),
    db: Session = Depends(get_db)
):

    # Only System Admin can delete roles
    if current_user["tenant_id"] is not None:
        raise HTTPException(
            status_code=403,
            detail="Only System Admin can delete roles"
        )

    role = db.query(Role).filter(
        Role.id == role_id
    ).first()

    if role is None:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )

    # Protect built-in system roles
    if role.name in ["SYSTEM_ADMIN", "TENANT_ADMIN"]:
        raise HTTPException(
            status_code=400,
            detail="System roles cannot be deleted"
        )

    deleted_role_name = role.name

    db.delete(role)

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action="ROLE_DELETED",
        resource_type="role",
        resource_id=role_id,
        details=f"Role {deleted_role_name} was deleted",
    )

    db.commit()

    return {
        "message": "Role deleted successfully"
    }


