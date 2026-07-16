# Deliverables Traceability

Maps every certification-challenge task deliverable to its exact location in this
repository. Live app: **https://prd.abhinay.app** · Loom: _<paste Loom link>_

---

## Task 1 — Problem

| Deliverable | Location |
|---|---|
| 1-sentence problem statement (no solution implied) | [`docs/01-problem-solution.md`](docs/01-problem-solution.md) § 1.1 |
| 1–2 paragraphs: who has it / what they do / how today / why not enough | `docs/01-problem-solution.md` § 1.2 |
| Current-state workflow diagram (steps, tools, pain points) | `docs/01-problem-solution.md` § 1.3 (Mermaid) |
| List of evaluation questions / input–output pairs | `docs/01-problem-solution.md` § 1.4 |

## Task 2 — Solution

| Deliverable | Location |
|---|---|
| 1-sentence solution | `docs/01-problem-solution.md` § 2.1 |
| Infrastructure diagram + one sentence per component | `docs/01-problem-solution.md` § 2.2 |
| Agent-workflow diagram + 1–2 paragraph explanation | `docs/01-problem-solution.md` § 2.3 |
| **LLM gateway** (required) | Helicone — [`api/llm.py`](api/llm.py) (`chat_client`, `_resolve_base_url`) |
| **Memory component** (required) | FAQ conversation history — [`api/agents/faq.py`](api/agents/faq.py) (`run_faq` `history`), [`api/prompts.py`](api/prompts.py) (`format_history_block`); PRD history — [`lib/history.ts`](lib/history.ts) |
| Runs in a browser on phone & laptop (required) | Next.js UI on Vercel — [`pages/`](pages/), live at https://prd.abhinay.app |

## Task 3 — Data

| Deliverable | Location |
|---|---|
| Default chunking strategy + rationale | [`docs/03-task3-data.md`](docs/03-task3-data.md); implementation [`api/rag/chunker.py`](api/rag/chunker.py) |
| Data source (RAG corpus) | [`data/pm_docs/`](data/pm_docs/) — 9 PM/PRD docs, 67 chunks; ingested via [`api/rag/ingest.py`](api/rag/ingest.py) into Qdrant |
| External API (agent tool) + role + interaction | Tavily — [`api/tools/tavily.py`](api/tools/tavily.py); interaction described in `docs/03-task3-data.md` |

## Task 4 — Prototype

| Deliverable | Location |
|---|---|
| End-to-end agentic RAG prototype | FAQ agent [`api/agents/faq.py`](api/agents/faq.py); PRD pipeline [`api/index.py`](api/index.py) + [`api/agents/`](api/agents/); UI [`pages/faq.tsx`](pages/faq.tsx), [`pages/product.tsx`](pages/product.tsx) |
| Deployed to a public endpoint | **https://prd.abhinay.app** (Vercel; routing [`vercel.json`](vercel.json)) |

## Task 5 — Eval Baseline

| Deliverable | Location |
|---|---|
| Test data set | [`eval/testset.json`](eval/testset.json) — 21 gold questions |
| Evaluation harness (retrieval + router + LLM-as-judge; optional RAGAS) | [`eval/run_eval.py`](eval/run_eval.py), [`eval/ragas_eval.py`](eval/ragas_eval.py) |
| Conclusions about pipeline performance | [`docs/02-task5-evaluation.md`](docs/02-task5-evaluation.md); raw results [`eval/report.md`](eval/report.md), [`eval/results.json`](eval/results.json) |

## Task 6 — Upgrades

| Deliverable | Location |
|---|---|
| Advanced retriever + why it helps | Retrieve-then-rerank — [`api/rag/rerank.py`](api/rag/rerank.py), [`api/rag/retriever.py`](api/rag/retriever.py) (`RAG_RERANK`); rationale in [`docs/04-task6-improvement.md`](docs/04-task6-improvement.md) |
| Performance comparison table | `docs/04-task6-improvement.md` (reproduce: `python -m eval.run_eval` vs `RAG_RERANK=1 python -m eval.run_eval`) |
| A second improvement + hard evidence | Model/generation layer — reasoning-effort control [`api/llm.py`](api/llm.py) (`chat_completion`) + tolerant output parsing [`api/models.py`](api/models.py); evidence in `docs/04-task6-improvement.md` |

## Task 7 — Next Steps

| Deliverable | Location |
|---|---|
| Reflection: keep vs. change for Demo Day, with reasoning | [`docs/05-task7-next-steps.md`](docs/05-task7-next-steps.md) |

---

## Requirements checklist

- ✅ LLM gateway of your choice — Helicone (`api/llm.py`)
- ✅ Memory component — FAQ conversation history + PRD history
- ✅ Runs on phone & laptop in a browser — Next.js on Vercel
- ✅ RAG over your own data — Qdrant + `data/pm_docs/`
- ✅ External search tool — Tavily (`api/tools/tavily.py`)
- ✅ Deployed to a public endpoint — https://prd.abhinay.app
