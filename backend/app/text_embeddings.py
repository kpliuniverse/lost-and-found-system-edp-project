from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME, trust_remote_code=True)


def embed_text(text: str, *, is_query: bool = False) -> list[float]:
    task_prefix = "search_query" if is_query else "search_document"
    embedding = get_model().encode(
        f"{task_prefix}: {text}",
        normalize_embeddings=True,
    )
    return embedding.tolist()
