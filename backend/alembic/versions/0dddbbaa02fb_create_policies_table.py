"""create policies table

Revision ID: 0dddbbaa02fb
Revises: 27df49a99935
Create Date: 2026-09-18
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0dddbbaa02fb"
down_revision: Union[str, Sequence[str], None] = "27df49a99935"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "policies",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False
        ),
        sa.Column(
            "name",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "description",
            sa.String(),
            nullable=True
        ),
        sa.Column(
            "data_type",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "severity",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False
        ),
        sa.Column(
            "tenant_id",
            sa.Integer(),
            sa.ForeignKey("tenants.id"),
            nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True
        )
    )

    op.create_index(
        "ix_policies_id",
        "policies",
        ["id"],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        "ix_policies_id",
        table_name="policies"
    )

    op.drop_table("policies")