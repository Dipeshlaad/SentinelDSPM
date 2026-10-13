"""add alert resolution fields

Revision ID: d35d96696bcd
Revises: c9baca09bae6
Create Date: 2026-09-20 07:43:21.153097

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d35d96696bcd"
down_revision: Union[str, Sequence[str], None] = "c9baca09bae6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "alerts",
        sa.Column(
            "resolved_at",
            sa.DateTime(timezone=True),
            nullable=True
        )
    )

    op.add_column(
        "alerts",
        sa.Column(
            "resolved_by_scan_id",
            sa.Integer(),
            nullable=True
        )
    )

    op.create_foreign_key(
        "fk_alerts_resolved_by_scan_id_scans",
        "alerts",
        "scans",
        ["resolved_by_scan_id"],
        ["id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_alerts_resolved_by_scan_id_scans",
        "alerts",
        type_="foreignkey"
    )

    op.drop_column(
        "alerts",
        "resolved_by_scan_id"
    )

    op.drop_column(
        "alerts",
        "resolved_at"
    )