"""add unique constraint to assets

Revision ID: e804ae6feb0f
Revises: 6f2bde5c6762
Create Date: 2026-09-16 04:41:26.175147

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e804ae6feb0f"
down_revision: Union[str, Sequence[str], None] = "6f2bde5c6762"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_assets_datasource_path",
        "assets",
        ["datasource_id", "path"]
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_assets_datasource_path",
        "assets",
        type_="unique"
    )