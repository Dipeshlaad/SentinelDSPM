"""create aws cloud accounts

Revision ID: 72ae5fe828e3
Revises: ea880bfc35aa
Create Date: 2026-09-22 16:57:13.929462

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72ae5fe828e3'
down_revision: Union[str, Sequence[str], None] = 'ea880bfc35aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        'aws_cloud_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('account_id', sa.String(), nullable=False),
        sa.Column('role_arn', sa.String(), nullable=False),
        sa.Column('external_id', sa.String(), nullable=False),
        sa.Column('region', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column(
            'last_verified_at',
            sa.DateTime(),
            nullable=True
        ),
        sa.Column(
            'created_at',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=True
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=True
        ),
        sa.ForeignKeyConstraint(
            ['tenant_id'],
            ['tenants.id']
        ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_aws_cloud_accounts_id'),
        'aws_cloud_accounts',
        ['id'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f('ix_aws_cloud_accounts_id'),
        table_name='aws_cloud_accounts'
    )

    op.drop_table(
        'aws_cloud_accounts'
    )