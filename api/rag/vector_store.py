"""Qdrant vector-store wrapper for the PM/PRD FAQ corpus.

Uses Qdrant Cloud (managed free tier). Configure with:
    QDRANT_URL        e.g. https://xxxx.cloud.qdrant.io:6333
    QDRANT_API_KEY    from the Qdrant Cloud console
    QDRANT_COLLECTION default "pm_prd_faq"
"""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass

from qdrant_client import QdrantClient  # type: ignore
from qdrant_client.models import (  # type: ignore
    Distance,
    PointStruct,
    VectorParams,
)

from api.rag.embeddings import EMBED_DIM

COLLECTION = os.environ.get("QDRANT_COLLECTION", "pm_prd_faq")


@dataclass
class Retrieved:
    text: str
    score: float
    source: str
    title: str
    heading: str


def get_client() -> QdrantClient:
    url = os.environ.get("QDRANT_URL")
    api_key = os.environ.get("QDRANT_API_KEY")
    if not url:
        raise RuntimeError("QDRANT_URL is not set. See RAG_SETUP.md.")
    return QdrantClient(url=url, api_key=api_key, timeout=30)


def ensure_collection(client: QdrantClient, *, recreate: bool = False) -> None:
    """Create the collection if it does not exist (or recreate it)."""
    exists = client.collection_exists(COLLECTION)
    if exists and recreate:
        client.delete_collection(COLLECTION)
        exists = False
    if not exists:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )


def upsert_chunks(
    client: QdrantClient,
    vectors: list[list[float]],
    payloads: list[dict],
) -> int:
    """Upsert embedded chunks. Returns the number of points written."""
    points = [
        PointStruct(id=str(uuid.uuid4()), vector=vec, payload=payload)
        for vec, payload in zip(vectors, payloads)
    ]
    client.upsert(collection_name=COLLECTION, points=points)
    return len(points)


def search(client: QdrantClient, query_vector: list[float], top_k: int = 5) -> list[Retrieved]:
    """Vector search. Returns the top_k most similar chunks."""
    hits = client.query_points(
        collection_name=COLLECTION,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    ).points
    results: list[Retrieved] = []
    for h in hits:
        p = h.payload or {}
        results.append(
            Retrieved(
                text=p.get("text", ""),
                score=float(h.score),
                source=p.get("source", ""),
                title=p.get("title", ""),
                heading=p.get("heading", ""),
            )
        )
    return results
