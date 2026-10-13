"""add tenant scoped user email uniqueness

Revision ID: 0fc46bd226e4
Revises: 9bbc068e5552
Create Date: 2026-09-14 02:33:08.330806

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '0fc46bd226e4'
down_revision: Union[str, Sequence[str], None] = '9bbc068e5552'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        'uq_user_email_tenant',
        'users',
        ['email', 'tenant_id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        'uq_user_email_tenant',
        'users',
        type_='unique'
    )