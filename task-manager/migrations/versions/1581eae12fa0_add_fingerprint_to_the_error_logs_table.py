"""add fingerprint to the error logs table

Revision ID: 1581eae12fa0
Revises: 16cb03e311e4
Create Date: 2026-07-22 10:28:55.935147

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1581eae12fa0'
down_revision: Union[str, Sequence[str], None] = '16cb03e311e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "error_logs",
        sa.Column("fingerprint", sa.String(length=64), nullable=True),
    )
    op.execute(
        "UPDATE error_logs SET fingerprint = 'legacy' WHERE fingerprint IS NULL"
    )
    op.alter_column(
        "error_logs",
        "fingerprint",
        nullable=False,
    )
    op.create_index(
        op.f("ix_error_logs_fingerprint"),
        "error_logs",
        ["fingerprint"],
        unique=False,
    )

def downgrade() -> None:
    op.drop_index(
        op.f("ix_error_logs_fingerprint"),
        table_name="error_logs",
    )

    op.drop_column("error_logs", "fingerprint")