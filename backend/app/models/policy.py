from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Policy(Base):
    __tablename__ = "policies"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=True
    )

    data_type = Column(
        String,
        nullable=False
    )

    severity = Column(
        String,
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

    