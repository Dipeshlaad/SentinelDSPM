from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    type = Column(
        String,
        nullable=False
    )

    path = Column(
        String,
        nullable=False
    )

    size = Column(
        Integer,
        nullable=True
    )

    datasource_id = Column(
        Integer,
        ForeignKey("datasources.id"),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    last_scanned_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    datasource = relationship(
        "Datasource"
    )