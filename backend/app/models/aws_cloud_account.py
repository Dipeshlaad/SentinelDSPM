from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class AWSCloudAccount(Base):

    __tablename__ = "aws_cloud_accounts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    tenant_id = Column(
        Integer,
        ForeignKey("tenants.id"),
        nullable=False
    )

    name = Column(
        String,
        nullable=False
    )

    account_id = Column(
        String,
        nullable=False
    )

    account_name = Column(
        String,
        nullable=False
    )

    role_name = Column(
        String,
        nullable=False
    )

    external_id = Column(
        String,
        nullable=False
    )

    region = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        nullable=False,
        default="pending"
    )

    last_verified_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )

    tenant = relationship(
        "Tenant",
        back_populates="aws_cloud_accounts"
    )