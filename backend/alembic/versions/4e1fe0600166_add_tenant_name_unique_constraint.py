"""add tenant name unique constraint

Revision ID: 4e1fe0600166
Revises: e9d4f5f6b048
Create Date: 2026-09-10 03:28:32.086848

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e1fe0600166'
down_revision: Union[str, Sequence[str], None] = 'e9d4f5f6b048'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        None,
        'tenants',
        ['name']
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        None,
        'tenants',
        type_='unique'
    )
