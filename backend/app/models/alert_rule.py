from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    UniqueConstraint
)
from sqlalchemy.sql import func

from app.database import Base


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    data_type = Column(
        String,
        nullable=False
    )

    threshold = Column(
        Integer,
        nullable=False
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "data_type",
            "threshold",
            name="uq_alert_rule_data_type_threshold"
        ),
    )

