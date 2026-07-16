"""Offline ingestion: load PM/PRD docs -> chunk -> embed -> upsert to Qdrant.

Run once (locally, not on Vercel) after setting the env vars in .env.local:

    python -m api.rag.ingest              # ingest data/pm_docs/*.md
    python -m api.rag.ingest --recreate   # wipe collection first
    python -m api.rag.ingest --path data/pm_docs

This is a build-time step. The deployed /api/faq endpoint only reads from
Qdrant, so ingestion never runs in the serverless function.
"""

from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv  # type: ignore

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(_ROOT, ".env.local"))

from api.rag.chunker import chunk_document, Chunk
from api.rag.embeddings import embed_texts
from api.rag import vector_store as vs

DEFAULT_DOCS_DIR = os.path.join(_ROOT, "data", "pm_docs")
EMBED_BATCH = 64


def _load_docs(path: str) -> list[tuple[str, str, str]]:
    """Return (source_filename, title, text) for every .md file under path."""
    docs: list[tuple[str, str, str]] = []
    for name in sorted(os.listdir(path)):
        if not name.endswith(".md"):
            continue
        full = os.path.join(path, name)
        with open(full, "r", encoding="utf-8") as f:
            text = f.read()
        # Title = first level-1 heading, else filename.
        title = name
        for line in text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        docs.append((name, title, text))
    return docs


def _batched(seq: list, n: int):
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def ingest(path: str, recreate: bool) -> None:
    docs = _load_docs(path)
    if not docs:
        print(f"No .md files found in {path}", file=sys.stderr)
        sys.exit(1)

    all_chunks: list[Chunk] = []
    for source, title, text in docs:
        chunks = chunk_document(text, source=source, title=title)
        all_chunks.extend(chunks)
        print(f"  {source}: {len(chunks)} chunks")

    print(f"Total: {len(all_chunks)} chunks from {len(docs)} documents")

    client = vs.get_client()
    vs.ensure_collection(client, recreate=recreate)

    written = 0
    for batch in _batched(all_chunks, EMBED_BATCH):
        vectors = embed_texts([c.text for c in batch])
        payloads = [
            {
                "text": c.text,
                "source": c.metadata["source"],
                "title": c.metadata["title"],
                "heading": c.metadata["heading"],
                "chunk_index": c.chunk_index,
            }
            for c in batch
        ]
        written += vs.upsert_chunks(client, vectors, payloads)
        print(f"  upserted {written}/{len(all_chunks)}")

    print(f"Done. {written} chunks in collection '{vs.COLLECTION}'.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest PM/PRD docs into Qdrant.")
    parser.add_argument("--path", default=DEFAULT_DOCS_DIR, help="Directory of .md docs")
    parser.add_argument("--recreate", action="store_true", help="Wipe collection first")
    args = parser.parse_args()
    ingest(args.path, args.recreate)


if __name__ == "__main__":
    main()
