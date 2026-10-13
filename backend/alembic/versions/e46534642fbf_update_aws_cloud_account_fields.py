"""update aws cloud account fields

Revision ID: e46534642fbf
Revises: 72ae5fe828e3
Create Date: 2026-09-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e46534642fbf'
down_revision: Union[str, Sequence[str], None] = '72ae5fe828e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        'aws_cloud_accounts',
        sa.Column(
            'account_name',
            sa.String(),
            nullable=False,
            server_default=''
        )
    )

    op.add_column(
        'aws_cloud_accounts',
        sa.Column(
            'role_name',
            sa.String(),
            nullable=False,
            server_default=''
        )
    )

    op.drop_column(
        'aws_cloud_accounts',
        'role_arn'
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.add_column(
        'aws_cloud_accounts',
        sa.Column(
            'role_arn',
            sa.String(),
            nullable=False,
            server_default=''
        )
    )

    op.drop_column(
        'aws_cloud_accounts',
        'role_name'
    )

    op.drop_column(
        'aws_cloud_accounts',
        'account_name'
    )