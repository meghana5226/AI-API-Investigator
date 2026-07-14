"""
Thin wrapper around a persistent ChromaDB instance. Each API project gets
its own collection (namespaced by project id) so semantic search never
leaks results across projects. The chromadb import and client creation
are deferred so the rest of the app can import/start without chromadb
installed (e.g. lightweight test runs); the client is created on first
real use.
"""
import logging
from functools import lru_cache
from typing import Any

from app.core.config import settings
from app.services.embedding_service import embed_query, embed_texts

logger = logging.getLogger(__name__)


@lru_cache
def _get_client():
    import chromadb
    from chromadb.config import Settings as ChromaSettings

    return chromadb.PersistentClient(
        path=settings.CHROMA_PERSIST_DIR,
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def _collection_name(project_id: str) -> str:
    return f"project_{str(project_id).replace('-', '')}"


def index_endpoints(project_id: str, endpoints: list[dict[str, Any]]) -> int:
    """Embeds and stores each endpoint's text representation in Chroma.
    Returns the number of chunks indexed."""
    collection = _get_client().get_or_create_collection(_collection_name(project_id))

    documents, metadatas, ids = [], [], []
    for i, ep in enumerate(endpoints):
        text = (
            f"{ep.get('method', '')} {ep.get('path', '')}\n"
            f"Summary: {ep.get('summary') or ''}\n"
            f"Description: {ep.get('description') or ''}\n"
            f"Tags: {', '.join(ep.get('tags') or [])}"
        )
        documents.append(text)
        metadatas.append({
            "method": ep.get("method", ""),
            "path": ep.get("path", ""),
            "summary": ep.get("summary") or "",
        })
        ids.append(f"{project_id}_{i}")

    if not documents:
        return 0

    embeddings = embed_texts(documents)
    collection.upsert(documents=documents, embeddings=embeddings, metadatas=metadatas, ids=ids)
    logger.info("Indexed %d chunks for project %s", len(documents), project_id)
    return len(documents)


def semantic_search(project_id: str, query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Returns the top_k most semantically similar endpoint chunks for a query."""
    try:
        collection = _get_client().get_collection(_collection_name(project_id))
    except Exception:
        logger.warning("No collection found for project %s", project_id)
        return []

    query_embedding = embed_query(query)
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    hits = []
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    for doc, meta, dist in zip(documents, metadatas, distances):
        hits.append({"text": doc, "metadata": meta, "distance": dist})
    return hits


def delete_project_index(project_id: str) -> None:
    try:
        _get_client().delete_collection(_collection_name(project_id))
    except Exception:
        logger.warning("Could not delete collection for project %s (may not exist)", project_id)
