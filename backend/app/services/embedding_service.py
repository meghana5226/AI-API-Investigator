"""
Wraps Sentence Transformers so the rest of the app doesn't need to know
which embedding model is in use. The model is loaded lazily and cached
as a module-level singleton to avoid reloading it on every request.
The import itself is deferred into the function so the rest of the app
can start up even in environments where the (heavy) ML dependency isn't
installed yet -- useful for lightweight test runs and fast CI checks.
"""
import logging
from functools import lru_cache
from typing import List

from app.core.config import settings

logger = logging.getLogger(__name__)


@lru_cache
def get_embedding_model():
    from sentence_transformers import SentenceTransformer

    logger.info("Loading embedding model: %s", settings.EMBEDDING_MODEL)
    return SentenceTransformer(settings.EMBEDDING_MODEL)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Returns a list of embedding vectors, one per input text."""
    if not texts:
        return []
    model = get_embedding_model()
    vectors = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return vectors.tolist()


def embed_query(query: str) -> List[float]:
    return embed_texts([query])[0]
