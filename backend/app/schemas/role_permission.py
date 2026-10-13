from pydantic import BaseModel
from typing import List


class RolePermissionCreate(BaseModel):
    role: str
    permissions: List[str]