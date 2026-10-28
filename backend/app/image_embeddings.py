from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Protocol

from PIL import Image

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/clip-ViT-B-32"


class ImageTextItem(Protocol):
    title: str
    description: str


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def embed_text_for_image(text: str) -> list[float]:
    embedding = get_model().encode(text, normalize_embeddings=True)
    return embedding.tolist()


def embed_image(image: Image.Image) -> list[float]:
    embedding = get_model().encode(image.convert("RGB"), normalize_embeddings=True)
    return embedding.tolist()


def gen_img_embedding_string(item: ImageTextItem) -> str:
    return f"{item.title}, {item.description}"