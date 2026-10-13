"""create alert rules

Revision ID: d3c158c2ed9a
Revises: 36bb08bf36c3
Create Date: 2026-09-20 07:03:40.657657

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d3c158c2ed9a"
down_revision: Union[str, Sequence[str], None] = "36bb08bf36c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "alert_rules",
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
            "is_active",
            sa.Boolean(),
            nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "data_type",
            "threshold",
            name="uq_alert_rule_data_type_threshold"
        )
    )

    op.create_index(
        op.f("ix_alert_rules_id"),
        "alert_rules",
        ["id"],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_alert_rules_id"),
        table_name="alert_rules"
    )

    op.drop_table("alert_rules")

