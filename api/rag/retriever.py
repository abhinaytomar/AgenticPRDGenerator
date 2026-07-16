"""Query-time retrieval over the Qdrant PM/PRD corpus.

Default: dense-embedding similarity search.
Advanced (RAG_RERANK=1): retrieve-then-rerank — fetch a larger candidate set,
then LLM-rerank down to top_k to improve context precision (see Task 6).
"""

from __future__ import annotations

import os

from api.rag.embeddings import embed_query
from api.rag import vector_store as vs

RERANK = os.environ.get("RAG_RERANK", "").lower() in ("1", "true", "yes", "on")
RERANK_FETCH = int(os.environ.get("RAG_RERANK_FETCH", "12"))


def retrieve(query: str, top_k: int = 5) -> list[vs.Retrieved]:
    """Embed the query and return the top_k most relevant corpus chunks.

    With RAG_RERANK enabled, fetches RERANK_FETCH candidates and reranks them
    down to top_k.
    """
    client = vs.get_client()
    query_vector = embed_query(query)

    if RERANK:
        from api.rag.rerank import rerank
        candidates = vs.search(client, query_vector, top_k=max(RERANK_FETCH, top_k))
        return rerank(query, candidates, top_n=top_k)

    return vs.search(client, query_vector, top_k=top_k)
