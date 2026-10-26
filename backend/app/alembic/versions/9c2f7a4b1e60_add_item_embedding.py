"""Add item embedding

Revision ID: 9c2f7a4b1e60
Revises: 4a63451fb44d
Create Date: 2026-10-26 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import VECTOR


# revision identifiers, used by Alembic.
revision: str = '9c2f7a4b1e60'
down_revision: Union[str, Sequence[str], None] = '4a63451fb44d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    zero_vector = "[" + ",".join("0" for _ in range(256)) + "]"
    op.add_column(
        'items',
        sa.Column(
            'embedding',
            VECTOR(256),
            server_default=sa.text(f"'{zero_vector}'::vector"),
            nullable=False,
        ),
    )
    op.alter_column('items', 'embedding', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('items', 'embedding')
