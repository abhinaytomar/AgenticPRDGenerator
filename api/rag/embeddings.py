"""Embedding helpers built on the shared LLM client."""

from __future__ import annotations

from api.llm import embed_client, EMBED_MODEL, EMBED_DIM

__all__ = ["embed_texts", "embed_query", "EMBED_MODEL", "EMBED_DIM"]


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of documents. Returns one vector per input string."""
    if not texts:
        return []
    client = embed_client()
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    # OpenAI returns items in input order.
    return [item.embedding for item in resp.data]


def embed_query(text: str) -> list[float]:
    """Embed a single query string."""
    return embed_texts([text])[0]
