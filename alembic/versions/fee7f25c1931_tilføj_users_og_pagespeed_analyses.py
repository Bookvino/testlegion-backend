"""Tilføj users og pagespeed_analyses

Revision ID: fee7f25c1931
Revises: 2c293ad9a7d8
Create Date: 2025-06-30 01:31:35.986959

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fee7f25c1931'
down_revision: Union[str, Sequence[str], None] = '2c293ad9a7d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
