"""create findings table

Revision ID: 27df49a99935
Revises: e804ae6feb0f
Create Date: 2026-09-16 05:55:05.646554

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "27df49a99935"
down_revision: Union[str, Sequence[str], None] = "e804ae6feb0f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "findings",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False
        ),

        sa.Column(
            "asset_id",
            sa.Integer(),
            sa.ForeignKey("assets.id"),
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
            nullable=False,
            default=1
        ),

        sa.Column(
            "severity",
            sa.String(),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True
        ),

        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True
        )
    )

    op.create_index(
        "ix_findings_id",
        "findings",
        ["id"],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        "ix_findings_id",
        table_name="findings"
    )

    op.drop_table("findings")