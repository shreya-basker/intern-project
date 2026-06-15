"""create users table

Revision ID: e4c57641fbb1
Revises: 
Create Date: 2026-06-15 10:54:23.795900

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4c57641fbb1'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users_alembic",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name",sa.Text(),nullable=False),
        sa.Column("email",sa.Text(),nullable=False, unique=True),
        sa.Column("age",sa.BigInteger())
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users_alembic")
