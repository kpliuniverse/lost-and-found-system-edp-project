"""added image embedding

Revision ID: d085d7bd71e6
Revises: 26b4f5520c08
Create Date: 2026-10-27 09:13:57.269576

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import VECTOR

# revision identifiers, used by Alembic.
revision: str = 'd085d7bd71e6'
down_revision: Union[str, Sequence[str], None] = '26b4f5520c08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'postimages',
        sa.Column('image_embedding', VECTOR(dim=512), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('postimages', 'image_embedding')
