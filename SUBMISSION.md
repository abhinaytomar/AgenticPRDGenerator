# PRD Generator — Certification Challenge Submission

An agentic PRD generator with a RAG-powered product-management FAQ assistant.

- **Live app:** https://prd.abhinay.app  (try `/faq` and `/product`)
- **Loom demo:** _<paste your Loom link here>_
- **Repo:** this repository

## Deliverables by task

| Task | Deliverable | Where |
|---|---|---|
| 1 | Problem, audience, current-state workflow diagram, eval questions | [`docs/01-problem-solution.md`](docs/01-problem-solution.md) |
| 2 | Solution, infrastructure diagram, agent-workflow diagram | [`docs/01-problem-solution.md`](docs/01-problem-solution.md) |
| 3 | Chunking strategy, data source + external API (Tavily) | [`docs/03-task3-data.md`](docs/03-task3-data.md) |
| 4 | End-to-end agentic RAG prototype, deployed to a public endpoint | live at https://prd.abhinay.app |
| 5 | Test set + evaluation harness + baseline conclusions | [`docs/02-task5-evaluation.md`](docs/02-task5-evaluation.md), [`eval/`](eval/) |
| 6 | Advanced retriever (rerank) + a second improvement, before/after | [`docs/04-task6-improvement.md`](docs/04-task6-improvement.md) |
| 7 | Reflection: keep vs. change for Demo Day | [`docs/05-task7-next-steps.md`](docs/05-task7-next-steps.md) |

## Architecture at a glance

- **Frontend:** Next.js 16 + React 19, Clerk auth (runs in-browser on phone & laptop)
- **Backend:** FastAPI on Vercel; custom multi-agent orchestration
- **LLM:** `gpt-5-nano` via the **Helicone** LLM gateway (also the monitoring tool)
- **RAG:** OpenAI `text-embedding-3-small` (1536-d) + **Qdrant Cloud** over a 9-doc PM/PRD knowledge base
- **Agent tool:** **Tavily** web search
- **Memory:** FAQ conversation history + saved PRD history
- **Evaluation:** custom harness (retrieval Hit@k/MRR, router accuracy, LLM-as-judge) + optional RAGAS

## Two workflows

1. **PRD pipeline:** intake → research → writer → critic → revision → human review → tickets.
2. **FAQ (Agentic RAG):** embed → retrieve (Qdrant) → router decides web-vs-corpus → optional Tavily → grounded, cited answer.

## Run locally

See [`RAG_SETUP.md`](RAG_SETUP.md) for setup and ingestion; [`eval/README.md`](eval/README.md) to run the evaluation.
