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


class ScanDetection(Base):

    __tablename__ = "scan_detections"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    scan_id = Column(
        Integer,
        ForeignKey("scans.id"),
        nullable=False
    )

    asset_id = Column(
        Integer,
        ForeignKey("assets.id"),
        nullable=False
    )

    data_type = Column(
        String,
        nullable=False
    )

    count = Column(
        Integer,
        nullable=False
    )

    policy_status = Column(
        String,
        nullable=False
    )

    detected_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    scan = relationship(
        "Scan"
    )

    asset = relationship(
        "Asset"
    )