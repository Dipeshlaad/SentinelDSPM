"""link datasources to aws cloud accounts

Revision ID: 6c4dfd32d3bf
Revises: e46534642fbf
Create Date: 2026-09-24 06:06:32.787681

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c4dfd32d3bf'
down_revision: Union[str, Sequence[str], None] = 'e46534642fbf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        'datasources',
        sa.Column(
            'aws_cloud_account_id',
            sa.Integer(),
            nullable=True
        )
    )

    op.create_foreign_key(
        'datasources_aws_cloud_account_id_fkey',
        'datasources',
        'aws_cloud_accounts',
        ['aws_cloud_account_id'],
        ['id']
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        'datasources_aws_cloud_account_id_fkey',
        'datasources',
        type_='foreignkey'
    )

    op.drop_column(
        'datasources',
        'aws_cloud_account_id'
    )