"""Query-time retrieval over the Qdrant PM/PRD corpus."""

from __future__ import annotations

from api.rag.embeddings import embed_query
from api.rag import vector_store as vs


def retrieve(query: str, top_k: int = 5) -> list[vs.Retrieved]:
    """Embed the query and return the top_k most relevant corpus chunks."""
    client = vs.get_client()
    query_vector = embed_query(query)
    return vs.search(client, query_vector, top_k=top_k)
