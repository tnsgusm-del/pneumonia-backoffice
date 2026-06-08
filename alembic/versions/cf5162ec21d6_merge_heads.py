"""merge heads

Revision ID: cf5162ec21d6
Revises: cb4e25603374, e18f87fa3f96
Create Date: 2026-06-06 19:40:19.112798

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf5162ec21d6'
down_revision: Union[str, Sequence[str], None] = ('cb4e25603374', 'e18f87fa3f96')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
