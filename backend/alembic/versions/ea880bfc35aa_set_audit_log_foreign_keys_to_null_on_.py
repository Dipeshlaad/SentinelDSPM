"""set audit log foreign keys to null on delete

Revision ID: ea880bfc35aa
Revises: 515622dbfa4a
Create Date: 2026-09-21 09:47:07.440890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea880bfc35aa'
down_revision: Union[str, Sequence[str], None] = '515622dbfa4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        "audit_logs_tenant_id_fkey",
        "audit_logs",
        type_="foreignkey",
    )

    op.drop_constraint(
        "audit_logs_user_id_fkey",
        "audit_logs",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "audit_logs_tenant_id_fkey",
        "audit_logs",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_foreign_key(
        "audit_logs_user_id_fkey",
        "audit_logs",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "audit_logs_tenant_id_fkey",
        "audit_logs",
        type_="foreignkey",
    )

    op.drop_constraint(
        "audit_logs_user_id_fkey",
        "audit_logs",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "audit_logs_tenant_id_fkey",
        "audit_logs",
        "tenants",
        ["tenant_id"],
        ["id"],
    )

    op.create_foreign_key(
        "audit_logs_user_id_fkey",
        "audit_logs",
        "users",
        ["user_id"],
        ["id"],
    )
