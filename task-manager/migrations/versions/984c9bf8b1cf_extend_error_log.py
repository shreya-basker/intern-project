"""extend error log

Revision ID: 984c9bf8b1cf
Revises: 162f1f83988f
Create Date: 2026-07-22 13:12:22.752636

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '984c9bf8b1cf'
down_revision: Union[str, Sequence[str], None] = '162f1f83988f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.add_column(
        "error_logs",
        sa.Column("summary", sa.Text(), nullable=True),
    )

    op.add_column(
        "error_logs",
        sa.Column("severity", sa.String(length=20), nullable=True),
    )

    op.add_column(
        "error_logs",
        sa.Column("confidence", sa.Float(), nullable=True),
    )


def downgrade():

    op.drop_column("error_logs", "confidence")
    op.drop_column("error_logs", "severity")
    op.drop_column("error_logs", "summary")