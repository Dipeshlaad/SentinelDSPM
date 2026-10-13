"""restore global user email uniqueness

Revision ID: 6dd946583aa3
Revises: 0fc46bd226e4
Create Date: 2026-09-14 03:33:17.756331
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '6dd946583aa3'
down_revision: Union[str, Sequence[str], None] = '0fc46bd226e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        'uq_user_email_tenant',
        'users',
        type_='unique'
    )

    op.create_unique_constraint(
        'users_email_key',
        'users',
        ['email']
    )


def downgrade() -> None:
    op.drop_constraint(
        'users_email_key',
        'users',
        type_='unique'
    )

    op.create_unique_constraint(
        'uq_user_email_tenant',
        'users',
        ['email', 'tenant_id']
    )
