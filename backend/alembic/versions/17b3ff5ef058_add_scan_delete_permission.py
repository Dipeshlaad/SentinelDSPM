"""add scan delete permission

Revision ID: 17b3ff5ef058
Revises: 6c4dfd32d3bf
Create Date: 2026-09-29 14:10:51.561737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17b3ff5ef058'
down_revision: Union[str, Sequence[str], None] = '6c4dfd32d3bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add scan:delete permission and assign it to admins."""

    op.execute(
        """
        INSERT INTO permissions (name)
        SELECT 'scan:delete'
        WHERE NOT EXISTS (
            SELECT 1
            FROM permissions
            WHERE name = 'scan:delete'
        )
        """
    )

    op.execute(
        """
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r
        CROSS JOIN permissions p
        WHERE r.name IN ('TENANT_ADMIN', 'SYSTEM_ADMIN')
          AND p.name = 'scan:delete'
          AND NOT EXISTS (
              SELECT 1
              FROM role_permissions rp
              WHERE rp.role_id = r.id
                AND rp.permission_id = p.id
          )
        """
    )


def downgrade() -> None:
    """Remove scan:delete permission and its role assignments."""

    op.execute(
        """
        DELETE FROM role_permissions
        WHERE permission_id = (
            SELECT id
            FROM permissions
            WHERE name = 'scan:delete'
        )
        """
    )

    op.execute(
        """
        DELETE FROM permissions
        WHERE name = 'scan:delete'
        """
    )