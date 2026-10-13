from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import role_permissions
from app.core.security import get_current_user


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def require_permission(permission_name: str):

    def permission_checker(
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

        role_id = current_user.get("role_id")

        permission = (
            db.query(Permission)
            .join(
                role_permissions,
                Permission.id == role_permissions.c.permission_id
            )
            .filter(
                role_permissions.c.role_id == role_id,
                Permission.name == permission_name
            )
            .first()
        )

        if permission is None:
            raise HTTPException(
                status_code=403,
                detail="Permission denied"
            )

        return current_user

    return permission_checker