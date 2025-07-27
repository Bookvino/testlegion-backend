"""Add is_verified field to User

Revision ID: e245448e52df
Revises: 6770083a6366
Create Date: 2025-07-23 18:48:06.750944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e245448e52df'
down_revision: Union[str, Sequence[str], None] = '6770083a6366'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Tilføj feltet 'is_verified' til users
    op.add_column(
        'users',
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false')
    )
    op.alter_column(
        'users',
        'email',
        existing_type=sa.VARCHAR(),
        nullable=False
    )
    op.alter_column(
        'users',
        'hashed_password',
        existing_type=sa.VARCHAR(),
        nullable=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'users',
        'hashed_password',
        existing_type=sa.VARCHAR(),
        nullable=True
    )
    op.alter_column(
        'users',
        'email',
        existing_type=sa.VARCHAR(),
        nullable=True
    )
    op.drop_column('users', 'is_verified')
