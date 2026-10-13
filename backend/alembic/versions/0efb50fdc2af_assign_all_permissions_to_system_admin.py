"""assign all permissions to system admin

Revision ID: 0efb50fdc2af
Revises: b81d8acbb094
Create Date: 2026-09-12 06:01:23.656124

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0efb50fdc2af'
down_revision: Union[str, Sequence[str], None] = 'b81d8acbb094'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r
        CROSS JOIN permissions p
        WHERE r.name = 'SYSTEM_ADMIN'
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DELETE FROM role_permissions
        WHERE role_id = (
            SELECT id
            FROM roles
            WHERE name = 'SYSTEM_ADMIN'
        )
        """
    )
