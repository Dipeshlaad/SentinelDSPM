from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    alert_rule_id = Column(
        Integer,
        ForeignKey("alert_rules.id"),
        nullable=False
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

    data_type = Column(String, nullable=False)
    threshold = Column(Integer, nullable=False)
    current_count = Column(Integer, nullable=False)
    severity = Column(String, nullable=False)

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    status = Column(
        String,
        nullable=False,
        default="OPEN"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    resolved_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    resolved_by_scan_id = Column(
        Integer,
        ForeignKey("scans.id"),
        nullable=True
    )

    alert_rule = relationship("AlertRule")
    scan = relationship(
        "Scan",
        foreign_keys=[scan_id]
    )
    asset = relationship("Asset")

    resolved_by_scan = relationship(
        "Scan",
        foreign_keys=[resolved_by_scan_id]
    )