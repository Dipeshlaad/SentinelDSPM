"""add user active status

Revision ID: 264840204d1a
Revises: 6dd946583aa3
Create Date: 2026-09-15 06:30:33.708194

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "264840204d1a"
down_revision: Union[str, Sequence[str], None] = "6dd946583aa3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "users",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true()
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "users",
        "is_active"
    )

