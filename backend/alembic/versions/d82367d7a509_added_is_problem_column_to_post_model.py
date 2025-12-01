"""added is_problem column to Post model

Revision ID: d82367d7a509
Revises: bac3d2ddec4e
Create Date: 2025-12-01 09:19:11.286863

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd82367d7a509'
down_revision: Union[str, Sequence[str], None] = 'bac3d2ddec4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
