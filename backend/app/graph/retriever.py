from qdrant_client import QdrantClient

from app.config import settings

EMBED_MODEL = "BAAI/bge-small-en-v1.5"  # doit rester identique à celui utilisé dans build_index.py

_client = QdrantClient(url=settings.qdrant_url)
_client.set_model(EMBED_MODEL)


def similarity_search(query: str, k: int = 5) -> list[dict]:
    """Retourne les k chunks les plus proches de `query` dans Qdrant."""
    results = _client.query(
        collection_name=settings.qdrant_collection,
        query_text=query,
        limit=k,
    )
    return [
        {
            "content": r.document,
            "source": r.metadata.get("source", "inconnu"),
        }
        for r in results
    ]
