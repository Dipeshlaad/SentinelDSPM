"""add tenant admin role

Revision ID: 913ee95f9343
Revises: 0efb50fdc2af
Create Date: 2026-09-12 06:24:26.421526

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '913ee95f9343'
down_revision: Union[str, Sequence[str], None] = '0efb50fdc2af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        INSERT INTO roles (name)
        VALUES ('TENANT_ADMIN')
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DELETE FROM roles
        WHERE name = 'TENANT_ADMIN'
        """
    )
