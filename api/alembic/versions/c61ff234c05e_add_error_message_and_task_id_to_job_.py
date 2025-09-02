"""Add error_message and task_id to job_runs

Revision ID: c61ff234c05e
Revises: d2941601bed9
Create Date: 2025-09-02 20:38:27.946433

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c61ff234c05e'
down_revision: Union[str, Sequence[str], None] = 'd2941601bed9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
