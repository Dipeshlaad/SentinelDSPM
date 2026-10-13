
"""create assets table

Revision ID: 6f2bde5c6762
Revises: 264840204d1a
Create Date: 2026-09-16 04:00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6f2bde5c6762"

down_revision: Union[str, Sequence[str], None] = "264840204d1a"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "assets",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "name",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "type",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "path",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "size",
            sa.Integer(),
            nullable=True
        ),
        sa.Column(
            "datasource_id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True
        ),
        sa.Column(
            "last_scanned_at",
            sa.DateTime(timezone=True),
            nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["datasource_id"],
            ["datasources.id"]
        ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        op.f("ix_assets_id"),
        "assets",
        ["id"],
        unique=False
    )


def downgrade() -> None:

    op.drop_index(
        op.f("ix_assets_id"),
        table_name="assets"
    )

    op.drop_table("assets")

