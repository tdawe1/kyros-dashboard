"""fix user model indexes and is_active default

Revision ID: 8b54a15498d5
Revises: abadf8c47608
Create Date: 2025-09-04 12:57:05.415165

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b54a15498d5'
down_revision: Union[str, Sequence[str], None] = 'abadf8c47608'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop redundant indexes (unique constraints already create indexes)
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    
    # Add server_default for is_active column
    # For SQLite, we need to recreate the column with the default
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("is_active", server_default="1")


def downgrade() -> None:
    """Downgrade schema."""
    # Remove server_default from is_active column
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("is_active", server_default=None)
    
    # Recreate the redundant indexes
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
