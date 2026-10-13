from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Tenant(Base):

    __tablename__ = "tenants"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False,
        unique=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    users = relationship(
        "User",
        back_populates="tenant"
    )

    aws_cloud_accounts = relationship(
    "AWSCloudAccount",
    back_populates="tenant"
    )