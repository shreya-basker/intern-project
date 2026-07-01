"""update role enum admin editor viewer

Revision ID: 1df23937c9e4
Revises: 8460a8b06c85
Create Date: 2026-06-18 12:06:34.026434

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '1df23937c9e4'
down_revision: str | Sequence[str] | None = '202bf1631a82'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Step 1: Add new column with no constraint
    op.add_column("users", sa.Column("role_new", sa.Text(), nullable=True))
 
    # Step 2: Migrate existing data
    op.execute("UPDATE users SET role_new = 'admin' WHERE role = 'admin'")
    op.execute("UPDATE users SET role_new = 'viewer' WHERE role != 'admin'")
 
    # Step 3: Set NOT NULL and add CHECK constraint
    op.alter_column("users", "role_new", nullable=False)
    op.create_check_constraint(
        "ck_users_role", "users",
        "role_new IN ('admin', 'editor', 'viewer')"
    )
 
    # Step 4: Drop old column, rename new one
    op.drop_column("users", "role")
    op.alter_column("users", "role_new", new_column_name="role")
 
def downgrade() -> None:
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.execute("UPDATE users SET role = 'user' WHERE role IN ('editor', 'viewer')"
    )
