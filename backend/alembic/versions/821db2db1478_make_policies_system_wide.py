"""make policies system wide

Revision ID: 821db2db1478
Revises: 0dddbbaa02fb
Create Date: 2026-09-18 13:39:32.788449

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "821db2db1478"
down_revision: Union[str, Sequence[str], None] = "0dddbbaa02fb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "policies_tenant_id_fkey",
        "policies",
        type_="foreignkey"
    )

    op.drop_column(
        "policies",
        "tenant_id"
    )


def downgrade() -> None:
    op.add_column(
        "policies",
        sa.Column(
            "tenant_id",
            sa.Integer(),
            nullable=True
        )
    )

    op.create_foreign_key(
        "policies_tenant_id_fkey",
        "policies",
        "tenants",
        ["tenant_id"],
        ["id"]
    )