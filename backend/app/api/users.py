
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database import get_db
from app.models.user import User
from app.models.role import Role
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserStatusUpdate,
)
from app.services.audit_service import create_audit_log
from app.core.security import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# ---------------------------------------------------------
# Helper: get current user's role
# ---------------------------------------------------------
def get_current_role(
    db: Session,
    current_user: dict,
):
    role = (
        db.query(Role)
        .filter(Role.id == current_user["role_id"])
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role",
        )

    return role


# ---------------------------------------------------------
# CREATE USER
# ---------------------------------------------------------
@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_role = get_current_role(
        db,
        current_user,
    )
    if current_role.name not in ("SYSTEM_ADMIN", "TENANT_ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can manage users",
        )

    current_user_role = current_role.name
    current_user_tenant_id = current_user["tenant_id"]

    if current_user_role != "SYSTEM_ADMIN":
        if user_data.tenant_id != current_user_tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create users in your own tenant",
            )

    role = (
        db.query(Role)
        .filter(Role.id == user_data.role_id)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role_id",
        )

    if (
        current_user_role != "SYSTEM_ADMIN"
        and role.name == "SYSTEM_ADMIN"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only System Admin can create a System Admin",
        )

    if role.name == "SYSTEM_ADMIN":
        if user_data.tenant_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="System Admin cannot belong to a tenant",
            )

    if role.name != "SYSTEM_ADMIN":
        if user_data.tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant users must belong to a tenant",
            )

    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    hashed_password = pwd_context.hash(
        user_data.password
    )

    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        tenant_id=user_data.tenant_id,
        role_id=user_data.role_id,
        is_active=True,
    )

    db.add(new_user)
    db.flush()

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action="USER_CREATED",
        resource_type="user",
        resource_id=new_user.id,
        details=f"User {new_user.email} was created",
    )

    db.commit()
    db.refresh(new_user)

    return new_user


# ---------------------------------------------------------
# GET ALL USERS
# ---------------------------------------------------------
@router.get(
    "/",
    response_model=list[UserResponse],
)
def get_users(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_role = get_current_role(
        db,
        current_user,
    )

    query = db.query(User)

    if current_role.name == "SYSTEM_ADMIN":
        return query.all()

    return (
        query
        .filter(
            User.tenant_id == current_user["tenant_id"]
        )
        .all()
    )


# ---------------------------------------------------------
# GET USER BY ID
# ---------------------------------------------------------
@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_role = get_current_role(
        db,
        current_user,
    )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if current_role.name == "SYSTEM_ADMIN":
        return user

    if user.tenant_id != current_user["tenant_id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


# ---------------------------------------------------------
# UPDATE USER
# ---------------------------------------------------------
@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_role = get_current_role(
        db,
        current_user,
    )
    if current_role.name not in ("SYSTEM_ADMIN", "TENANT_ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can manage users",
        )

    current_user_role = current_role.name

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if current_user_role != "SYSTEM_ADMIN":
        if user.tenant_id != current_user["tenant_id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

    if user_data.email is not None:
        existing_user = (
            db.query(User)
            .filter(
                User.email == user_data.email,
                User.id != user_id,
            )
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        user.email = user_data.email

    if user_data.password is not None:
        user.hashed_password = pwd_context.hash(
            user_data.password
        )

    if user_data.role_id is not None:
        role = (
            db.query(Role)
            .filter(Role.id == user_data.role_id)
            .first()
        )

        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role_id",
            )

        if (
            role.name == "SYSTEM_ADMIN"
            and current_user_role != "SYSTEM_ADMIN"
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only System Admin can assign System Admin role",
            )

        if role.name == "SYSTEM_ADMIN":
            user.tenant_id = None

        user.role_id = role.id

    if user_data.tenant_id is not None:
        if current_user_role != "SYSTEM_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only System Admin can change tenant assignment",
            )

        target_role = (
            db.query(Role)
            .filter(Role.id == user.role_id)
            .first()
        )

        if (
            target_role
            and target_role.name == "SYSTEM_ADMIN"
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="System Admin cannot belong to a tenant",
            )

        user.tenant_id = user_data.tenant_id

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action="USER_UPDATED",
        resource_type="user",
        resource_id=user.id,
        details=f"User {user.email} was updated",
    )

    db.commit()
    db.refresh(user)

    return user


# ---------------------------------------------------------
# UPDATE USER STATUS
# ---------------------------------------------------------
@router.patch(
    "/{user_id}/status",
    response_model=UserResponse,
)
def update_user_status(
    user_id: int,
    status_data: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_role = get_current_role(
        db,
        current_user,
    )
    if current_role.name not in ("SYSTEM_ADMIN", "TENANT_ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can manage users",
        )

    current_user_role = current_role.name

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if current_user_role != "SYSTEM_ADMIN":
        if user.tenant_id != current_user["tenant_id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

    target_role = (
        db.query(Role)
        .filter(Role.id == user.role_id)
        .first()
    )

    if not target_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user role",
        )

    if target_role.name == "SYSTEM_ADMIN":
        if current_user_role != "SYSTEM_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only System Admin can modify a System Admin",
            )

        if not status_data.is_active:
            active_system_admins = (
                db.query(User)
                .join(Role)
                .filter(
                    Role.name == "SYSTEM_ADMIN",
                    User.is_active.is_(True),
                )
                .count()
            )

            if active_system_admins <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot deactivate the last active System Admin",
                )

    if (
        target_role.name == "TENANT_ADMIN"
        and not status_data.is_active
    ):
        active_tenant_admins = (
            db.query(User)
            .join(Role)
            .filter(
                Role.name == "TENANT_ADMIN",
                User.tenant_id == user.tenant_id,
                User.is_active.is_(True),
            )
            .count()
        )

        if active_tenant_admins <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate the last active Tenant Admin",
            )

    user.is_active = status_data.is_active

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action="USER_STATUS_CHANGED",
        resource_type="user",
        resource_id=user.id,
        details=f"User {user.email} status changed to {user.is_active}",
    )

    db.commit()
    db.refresh(user)

    return user


# ---------------------------------------------------------
# DELETE USER
# ---------------------------------------------------------
@router.delete(
    "/{user_id}"
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_role = get_current_role(
        db,
        current_user,
    )
    if current_role.name not in ("SYSTEM_ADMIN", "TENANT_ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can manage users",
        )

    current_user_role = current_role.name

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if current_user_role != "SYSTEM_ADMIN":
        if user.tenant_id != current_user["tenant_id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

    target_role = (
        db.query(Role)
        .filter(Role.id == user.role_id)
        .first()
    )

    if not target_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user role",
        )

    if target_role.name == "SYSTEM_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System Admin cannot be deleted",
        )

    if target_role.name == "TENANT_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant Admin cannot be deleted",
        )

    deleted_user_email = user.email

    db.delete(user)

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action="USER_DELETED",
        resource_type="user",
        resource_id=user_id,
        details=f"User {deleted_user_email} was deleted",
    )

    db.commit()

    return {
        "message": "User deleted successfully",
        "user_id": user_id,
    }

