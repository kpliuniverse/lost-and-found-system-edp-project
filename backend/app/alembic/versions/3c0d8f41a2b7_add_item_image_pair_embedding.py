"""Add and backfill item image-pair embeddings.

Revision ID: 3c0d8f41a2b7
Revises: d085d7bd71e6
Create Date: 2026-10-27

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import VECTOR

from app.image_embeddings import embed_text_for_image, gen_img_embedding_string


revision: str = "3c0d8f41a2b7"
down_revision: Union[str, Sequence[str], None] = "d085d7bd71e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class _ItemText:
    def __init__(self, title: str, description: str) -> None:
        self.title = title
        self.description = description


def upgrade() -> None:
    op.add_column(
        "items",
        sa.Column("image_pair_embedding", VECTOR(512), nullable=True),
    )

    connection = op.get_bind()
    item_rows = connection.execute(
        sa.text("SELECT id, title, description FROM items ORDER BY id")
    ).all()
    items_table = sa.table(
        "items",
        sa.column("id", sa.Integer),
        sa.column("image_pair_embedding", VECTOR(512)),
    )

    for row in item_rows:
        item = _ItemText(title=row.title, description=row.description)
        embedding = embed_text_for_image(gen_img_embedding_string(item))
        connection.execute(
            items_table.update()
            .where(items_table.c.id == row.id)
            .values(image_pair_embedding=embedding)
        )

    op.alter_column("items", "image_pair_embedding", nullable=False)


def downgrade() -> None:
    op.drop_column("items", "image_pair_embedding")
