from pydantic import BaseModel, EmailStr


class SystemAdminBootstrap(BaseModel):
    email: EmailStr
    password: str