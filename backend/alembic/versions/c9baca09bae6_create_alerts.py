
"""create alerts

Revision ID: c9baca09bae6
Revises: d3c158c2ed9a
Create Date: 2026-09-20 07:35:30.821305

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c9baca09bae6"

down_revision: Union[str, Sequence[str], None] = "d3c158c2ed9a"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "alerts",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "alert_rule_id",
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
            "threshold",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "current_count",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "severity",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "title",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "description",
            sa.String(),
            nullable=True
        ),
        sa.Column(
            "status",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["alert_rule_id"],
            ["alert_rules.id"]
        ),
        sa.ForeignKeyConstraint(
            ["scan_id"],
            ["scans.id"]
        ),
        sa.ForeignKeyConstraint(
            ["asset_id"],
            ["assets.id"]
        ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        op.f("ix_alerts_id"),
        "alerts",
        ["id"],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_alerts_id"),
        table_name="alerts"
    )

    op.drop_table("alerts")

