
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import role_permissions
from app.schemas.role_permission import RolePermissionCreate
from app.core.permissions import require_permission
from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/api/v1/role-permissions",
    tags=["Role Permissions"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# Set permissions for a role
@router.post("/")
def set_role_permissions(
    data: RolePermissionCreate,
    current_user=Depends(
        require_permission("tenant:update")
    ),
    db: Session = Depends(get_db)
):

    # Only System Admin can manage role permissions
    if current_user["tenant_id"] is not None:
        raise HTTPException(
            status_code=403,
            detail="Only System Admin can manage role permissions"
        )

    # Find role by name
    role = db.query(Role).filter(
        Role.name == data.role
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
            detail="System roles cannot have their permissions modified"
        )

    # Remove duplicate permission names
    permission_names = list(
        dict.fromkeys(data.permissions)
    )

    # Find permissions by name
    permissions = db.query(Permission).filter(
        Permission.name.in_(permission_names)
    ).all()

    found_names = {
        permission.name
        for permission in permissions
    }

    # Check for invalid permissions
    missing_permissions = [
        name
        for name in permission_names
        if name not in found_names
    ]

    if missing_permissions:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Permission not found",
                "permissions": missing_permissions
            }
        )

    # Get currently assigned permissions
    current_permissions = db.query(Permission).join(
        role_permissions,
        Permission.id == role_permissions.c.permission_id
    ).filter(
        role_permissions.c.role_id == role.id
    ).all()

    current_permission_names = {
        permission.name
        for permission in current_permissions
    }

    new_permission_names = {
        permission.name
        for permission in permissions
    }

    # Determine permission changes
    assigned_permissions = (
        new_permission_names - current_permission_names
    )

    removed_permissions = (
        current_permission_names - new_permission_names
    )

    # Remove existing permissions for role
    db.execute(
        role_permissions.delete().where(
            role_permissions.c.role_id == role.id
        )
    )

    # Add new permissions
    for permission in permissions:

        db.execute(
            role_permissions.insert().values(
                role_id=role.id,
                permission_id=permission.id
            )
        )

    # Audit newly assigned permissions
    for permission_name in assigned_permissions:

        permission = next(
            permission
            for permission in permissions
            if permission.name == permission_name
        )

        create_audit_log(
            db=db,
            user_id=current_user["user_id"],
            tenant_id=current_user["tenant_id"],
            action="ROLE_PERMISSION_ASSIGNED",
            resource_type="role_permission",
            resource_id=permission.id,
            details=(
                f"Permission {permission_name} "
                f"was assigned to role {role.name}"
            ),
        )

    # Audit removed permissions
    for permission_name in removed_permissions:

        permission = next(
            permission
            for permission in current_permissions
            if permission.name == permission_name
        )

        create_audit_log(
            db=db,
            user_id=current_user["user_id"],
            tenant_id=current_user["tenant_id"],
            action="ROLE_PERMISSION_REMOVED",
            resource_type="role_permission",
            resource_id=permission.id,
            details=(
                f"Permission {permission_name} "
                f"was removed from role {role.name}"
            ),
        )

    db.commit()

    return {
        "message": "Role permissions updated successfully",
        "role": role.name,
        "permissions": [
            permission.name
            for permission in permissions
        ]
    }


# Get permissions assigned to role
@router.get("/{role_name}")
def get_role_permissions(
    role_name: str,
    current_user=Depends(
        require_permission("tenant:read")
    ),
    db: Session = Depends(get_db)
):

    role = db.query(Role).filter(
        Role.name == role_name
    ).first()

    if role is None:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )

    permissions = db.query(Permission).join(
        role_permissions,
        Permission.id == role_permissions.c.permission_id
    ).filter(
        role_permissions.c.role_id == role.id
    ).all()

    return {
        "role": role.name,
        "permissions": [
            permission.name
            for permission in permissions
        ]
    }
