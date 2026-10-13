from sqlalchemy import Column, Integer, String
from app.models.role_permission import role_permissions
from sqlalchemy.orm import relationship

from app.database import Base


class Role(Base):

    __tablename__ = "roles"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String,
        unique=True,
        nullable=False
    )

    users = relationship(
        "User",
        back_populates="role"
    )

    permissions = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles"
    )