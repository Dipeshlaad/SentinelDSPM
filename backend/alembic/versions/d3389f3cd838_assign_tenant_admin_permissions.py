"""assign tenant admin permissions

Revision ID: d3389f3cd838
Revises: 913ee95f9343
Create Date: 2026-09-12 06:27:30.606652

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3389f3cd838'
down_revision: Union[str, Sequence[str], None] = '913ee95f9343'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r
        JOIN permissions p
            ON p.name IN (
                'tenant:read',
                'user:read',
                'user:create',
                'user:update',
                'user:delete',
                'datasource:read',
                'datasource:create',
                'datasource:update',
                'datasource:delete',
                'scan:read',
                'scan:create',
                'scan:cancel',
                'finding:read',
                'finding:update',
                'report:read',
                'report:create',
                'policy:read',
                'policy:create',
                'policy:update',
                'policy:delete'
            )
        WHERE r.name = 'TENANT_ADMIN'
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
            WHERE name = 'TENANT_ADMIN'
        )
        """
    )