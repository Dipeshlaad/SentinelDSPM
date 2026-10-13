import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel
from jose import jwt

from app.database import SessionLocal
from app.models.user import User
from app.core.security import (
    SECRET_KEY,
    ALGORITHM,
    get_current_user
)


# Load environment variables
load_dotenv()


ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "60"
    )
)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(data: LoginRequest):

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.email == data.email)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=401,
                detail="User account is inactive"
            )

        password_valid = pwd_context.verify(
            data.password,
            user.hashed_password
        )

        if not password_valid:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        token_data = {
            "user_id": user.id,
            "email": user.email,
            "tenant_id": user.tenant_id,
            "role_id": user.role_id,
            "exp": datetime.now(timezone.utc)
            + timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )
        }

        access_token = jwt.encode(
            token_data,
            SECRET_KEY,
            algorithm=ALGORITHM
        )

        return {
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer"
        }

    finally:
        db.close()


@router.get("/me")
def get_me(
    current_user=Depends(get_current_user)
):
    return current_user


