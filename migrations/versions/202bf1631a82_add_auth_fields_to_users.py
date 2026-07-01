"""add auth fields to users

Revision ID: 202bf1631a82
Revises: e4c57641fbb1
Create Date: 2026-06-15 15:18:57.904840

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "202bf1631a82"
down_revision: str | Sequence[str] | None = "e4c57641fbb1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("hashed_password", sa.String(), nullable=True))

    op.add_column("users", sa.Column("role", sa.String(), nullable=True, server_default="user"))


def downgrade() -> None:
    op.drop_column("users", "role")
    op.drop_column("users", "hashed_password")
