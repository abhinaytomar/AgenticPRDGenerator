"""Advanced retrieval: LLM-based reranking (retrieve-then-rerank).

The Task 5 baseline showed retrieval recall was maxed (Hit@k = MRR = 1.00) but
context precision was only 0.63 — the top-k contained ~37% off-topic chunks. A
reranker fixes exactly that: fetch a *larger* candidate set by embedding
similarity, then have the model re-order them by true relevance and keep only the
best few. This trims noise from the context the answer model sees.

We use an LLM reranker (via the existing gateway) rather than a cross-encoder so
there are no heavy ML dependencies (torch/sentence-transformers) — important for
serverless deployment on Vercel.

Enabled with RAG_RERANK=1 (see api/rag/retriever.py).
"""

from __future__ import annotations

import json

from api.llm import chat_completion

RERANK_SYSTEM = """You are a search reranker. Given a user question and a list of numbered
passages, rank the passages by how directly and completely they answer the question.
Return valid JSON only, listing passage indices from most to least relevant:
{"ranking": [3, 0, 5, ...]}
Include every index exactly once."""


def rerank(query: str, candidates: list, top_n: int) -> list:
    """Rerank candidate chunks by relevance to the query; return the top_n.

    `candidates` is a list of Retrieved objects (must have `.text`). Falls back
    to the original order on any parsing failure.
    """
    if len(candidates) <= top_n:
        return candidates

    passages = "\n\n".join(f"[{i}] {c.text[:400]}" for i, c in enumerate(candidates))
    user_msg = f"Question:\n{query}\n\nPassages:\n{passages}\n\nRank all passage indices."

    try:
        resp = chat_completion(
            messages=[
                {"role": "system", "content": RERANK_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
        )
        order = json.loads(resp.choices[0].message.content).get("ranking", [])
    except Exception:  # noqa: BLE001 - reranking is best-effort
        return candidates[:top_n]

    seen: set = set()
    picked: list = []
    for i in order:
        if isinstance(i, int) and 0 <= i < len(candidates) and i not in seen:
            seen.add(i)
            picked.append(candidates[i])
        if len(picked) >= top_n:
            break
    # Backfill from original order if the model returned too few valid indices.
    for i, c in enumerate(candidates):
        if len(picked) >= top_n:
            break
        if i not in seen:
            picked.append(c)
            seen.add(i)
    return picked[:top_n]
