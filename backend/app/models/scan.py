from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Scan(Base):

    __tablename__ = "scans"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String,
        nullable=False
    )

    datasource_id = Column(
        Integer,
        ForeignKey("datasources.id"),
        nullable=False
    )

    status = Column(
        String,
        nullable=False,
        default="pending"
    )

    started_at = Column(
        DateTime,
        nullable=True
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    datasource = relationship(
        "Datasource"
    )