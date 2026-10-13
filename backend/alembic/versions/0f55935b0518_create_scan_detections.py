"""create scan detections

Revision ID: 0f55935b0518
Revises: 8e4c3787ab66
Create Date: 2026-09-20 03:02:16.667933

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0f55935b0518"
down_revision: Union[str, Sequence[str], None] = "8e4c3787ab66"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "scan_detections",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "scan_id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "asset_id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "data_type",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "count",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "policy_status",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "detected_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["asset_id"],
            ["assets.id"]
        ),
        sa.ForeignKeyConstraint(
            ["scan_id"],
            ["scans.id"]
        ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        "ix_scan_detections_id",
        "scan_detections",
        ["id"],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        "ix_scan_detections_id",
        table_name="scan_detections"
    )

    op.drop_table(
        "scan_detections"
    )