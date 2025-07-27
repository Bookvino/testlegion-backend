"""Add is_verified field to User

Revision ID: 308f345d9f52
Revises: e245448e52df
Create Date: 2025-07-23 22:12:49.629314

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '308f345d9f52'
down_revision: Union[str, Sequence[str], None] = 'e245448e52df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
