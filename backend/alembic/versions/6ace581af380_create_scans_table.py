"""create scans table

Revision ID: 6ace581af380
Revises: 182c3d7dfddd
Create Date: 2026-09-12 03:21:34.081477

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ace581af380'
down_revision: Union[str, Sequence[str], None] = '182c3d7dfddd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "scans",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True
        ),
        sa.Column(
            "name",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "datasource_id",
            sa.Integer(),
            sa.ForeignKey("datasources.id"),
            nullable=False
        ),
        sa.Column(
            "status",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "started_at",
            sa.DateTime(),
            nullable=True
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(),
            nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("scans")