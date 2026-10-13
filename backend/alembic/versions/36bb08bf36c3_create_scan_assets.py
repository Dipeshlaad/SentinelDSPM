"""create scan assets

Revision ID: 36bb08bf36c3
Revises: 0f55935b0518
Create Date: 2026-09-20 04:39:18.616456

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "36bb08bf36c3"
down_revision: Union[str, Sequence[str], None] = "0f55935b0518"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "scan_assets",

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
        op.f("ix_scan_assets_id"),
        "scan_assets",
        ["id"],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_scan_assets_id"),
        table_name="scan_assets"
    )

    op.drop_table(
        "scan_assets"
    )