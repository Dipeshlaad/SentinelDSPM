"""add tenant created_at default

Revision ID: 3b12f298d624
Revises: 4e1fe0600166
Create Date: 2026-09-10 03:48:44.014550

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b12f298d624'
down_revision: Union[str, Sequence[str], None] = '4e1fe0600166'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'tenants',
        'created_at',
        server_default=sa.text('now()'),
        existing_type=sa.DateTime(),
        existing_nullable=True
    )


def downgrade() -> None:
    op.alter_column(
        'tenants',
        'created_at',
        server_default=None,
        existing_type=sa.DateTime(),
        existing_nullable=True
    )
