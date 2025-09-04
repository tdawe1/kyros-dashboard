"""update_is_active_server_default_to_text

Revision ID: c16925234eb1
Revises: 8b54a15498d5
Create Date: 2025-09-04 13:17:54.247093

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c16925234eb1'
down_revision: Union[str, Sequence[str], None] = '8b54a15498d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Update is_active server_default to use proper SQL text
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("is_active", server_default=sa.text("true"))


def downgrade() -> None:
    """Downgrade schema."""
    # Revert is_active server_default to previous value
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("is_active", server_default="1")
