from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Datasource(Base):

    __tablename__ = "datasources"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String,
        nullable=False
    )

    type = Column(
        String,
        nullable=False
    )

    tenant_id = Column(
        Integer,
        ForeignKey("tenants.id"),
        nullable=False
    )

    aws_cloud_account_id = Column(
        Integer,
        ForeignKey("aws_cloud_accounts.id"),
        nullable=True
    )

    status = Column(
        String,
        nullable=False,
        default="active"
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    tenant = relationship(
        "Tenant"
    )