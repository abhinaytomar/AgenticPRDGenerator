# Agentic RAG FAQ — Setup

This adds a **PM/PRD FAQ** feature to the app: an agentic RAG assistant that
answers product-management questions grounded in a curated knowledge base
(RAG over Qdrant) and, when needed, a live web search (Tavily). Every LLM call
routes through a configurable **LLM gateway**.

## 1. New environment variables

Add these to `.env.local` (see `.env.example` for the full list):

```bash
# ── LLM gateway (Task 2 requirement) ──────────────────────────────
# Route all chat calls through a gateway. Example: OpenRouter.
LLM_GATEWAY_BASE_URL=https://openrouter.ai/api/v1
LLM_GATEWAY_API_KEY=sk-or-...            # your gateway key
LLM_CHAT_MODEL=openai/gpt-5-nano         # model id as the gateway expects it
# If LLM_GATEWAY_BASE_URL is unset, calls fall back to OpenAI directly.

# ── Embeddings (used for RAG ingestion + retrieval) ───────────────
OPENAI_API_KEY=sk-...                    # used for embeddings
EMBED_MODEL=text-embedding-3-small       # 1536-dim (default)
EMBED_DIM=1536

# ── Qdrant Cloud (managed free tier) ──────────────────────────────
QDRANT_URL=https://xxxxxxxx.cloud.qdrant.io:6333
QDRANT_API_KEY=...                       # from the Qdrant Cloud console
QDRANT_COLLECTION=pm_prd_faq

# ── Tavily (public web search tool) ───────────────────────────────
TAVILY_API_KEY=tvly-...                  # from tavily.com
```

Notes:
- The **gateway** is optional to run locally (it falls back to OpenAI), but the
  certification requires one — set `LLM_GATEWAY_BASE_URL` to satisfy it.
  OpenRouter, Portkey, and LiteLLM all expose an OpenAI-compatible base URL.
- Embeddings go to OpenAI by default; set `EMBED_GATEWAY_BASE_URL` to route them
  through a gateway that supports the embeddings route.
- If `TAVILY_API_KEY` is unset, the FAQ still works using the knowledge base
  only (the router simply never selects web search).

## 2. Install dependencies

```bash
pip install -r requirements.txt      # adds qdrant-client, tavily-python
```

## 3. Create a Qdrant Cloud cluster

1. Sign up at https://cloud.qdrant.io and create a free cluster.
2. Copy the cluster URL and an API key into `.env.local`.

## 4. Ingest the knowledge base (one-time, local)

The corpus lives in `data/pm_docs/` (9 PM/PRD best-practice documents). Run:

```bash
python -m api.rag.ingest --recreate
```

This chunks the docs (~1000-char recursive, heading-aware, 150 overlap),
embeds them, and upserts to the `pm_prd_faq` collection. Re-run without
`--recreate` to add documents. To use your own corpus, drop `.md` files into
`data/pm_docs/` (or pass `--path`) and re-run.

Ingestion is a **build-time step** — it never runs inside the deployed
serverless function. The `/api/faq` endpoint only reads from Qdrant at query time.

## 5. Run

```bash
npm run dev                          # Next.js on :3000
uvicorn api.index:app --port 8000    # FastAPI (separate terminal, local dev)
```

Open `/faq`, sign in, and ask a question. On Vercel, the FastAPI backend is
deployed as a serverless function automatically; set the same env vars in the
Vercel project settings.

## How the feature works

1. **Retrieve** — the question is embedded and the top-5 corpus chunks are
   pulled from Qdrant (RAG).
2. **Route** — a router LLM decides whether the corpus is sufficient or a web
   search is also warranted (the agent's decision point).
3. **Search** — if warranted, the Tavily tool fetches public results.
4. **Answer** — a synthesis LLM writes a grounded answer with inline `[n]`
   citations mapping to the numbered corpus/web sources. Recent conversation
   turns are threaded in as memory for follow-ups.

Every step is traced (latency / tokens / cost) via the existing observability
layer and returned in `meta`.

## Files added / changed

- `api/llm.py` — centralized gateway client (chat + embeddings)
- `api/rag/` — `chunker.py`, `embeddings.py`, `vector_store.py`, `ingest.py`, `retriever.py`
- `api/tools/tavily.py` — Tavily web-search tool
- `api/agents/faq.py` — the FAQ agentic-RAG agent
- `api/index.py` — new `POST /api/faq` endpoint; legacy + agents routed via gateway
- `api/models.py`, `api/prompts.py` — FAQ schemas + prompts
- `data/pm_docs/*.md` — the knowledge-base corpus
- `pages/faq.tsx`, `lib/api.ts`, `lib/types.ts`, `pages/index.tsx` — FAQ chat UI
- `requirements.txt` — `qdrant-client`, `tavily-python`
