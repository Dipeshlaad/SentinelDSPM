"""add system admin role

Revision ID: b81d8acbb094
Revises: 3bf35a8eb899
Create Date: 2026-09-12 05:57:39.153600

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b81d8acbb094'
down_revision: Union[str, Sequence[str], None] = '3bf35a8eb899'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        INSERT INTO roles (name)
        VALUES ('SYSTEM_ADMIN')
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DELETE FROM roles
        WHERE name = 'SYSTEM_ADMIN'
        """
    )