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


class Finding(Base):
    __tablename__ = "findings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
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
        nullable=False,
        default=1
    )

    severity = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    last_seen_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    asset = relationship(
        "Asset"
    )