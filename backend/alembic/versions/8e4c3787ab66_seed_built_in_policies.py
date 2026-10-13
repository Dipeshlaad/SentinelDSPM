"""seed built in policies

Revision ID: 8e4c3787ab66
Revises: 821db2db1478
Create Date: 2026-09-18 14:14:31.836286

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8e4c3787ab66"
down_revision: Union[str, Sequence[str], None] = "821db2db1478"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    policies_table = sa.table(
        "policies",
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("data_type", sa.String),
        sa.column("severity", sa.String),
        sa.column("is_active", sa.Boolean),
    )

    op.bulk_insert(
        policies_table,
        [
            {
                "name": "Email Address Protection",
                "description": "Detects email addresses stored in supported data sources.",
                "data_type": "email",
                "severity": "medium",
                "is_active": True,
            },
            {
                "name": "Phone Number Protection",
                "description": "Detects phone numbers stored in supported data sources.",
                "data_type": "phone",
                "severity": "medium",
                "is_active": True,
            },
            {
                "name": "Aadhaar Protection",
                "description": "Detects Aadhaar numbers stored in supported data sources.",
                "data_type": "aadhaar",
                "severity": "high",
                "is_active": True,
            },
            {
                "name": "PAN Protection",
                "description": "Detects PAN numbers stored in supported data sources.",
                "data_type": "pan",
                "severity": "high",
                "is_active": True,
            },
            {
                "name": "Credit Card Protection",
                "description": "Detects credit card numbers stored in supported data sources.",
                "data_type": "credit_card",
                "severity": "critical",
                "is_active": True,
            },
            {
                "name": "AWS Access Key Protection",
                "description": "Detects AWS access keys stored in supported data sources.",
                "data_type": "aws_access_key",
                "severity": "critical",
                "is_active": True,
            },
        ],
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM policies
        WHERE data_type IN (
            'email',
            'phone',
            'aadhaar',
            'pan',
            'credit_card',
            'aws_access_key'
        )
        """
    )