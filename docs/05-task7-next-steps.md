# Task 7 — Next Steps

Reflecting on what I've built, here's what I plan to keep for Demo Day and what
I'd change or improve, with reasoning.

## What I'll keep

- **The agentic RAG FAQ.** The evaluation showed it is faithful (0.94) and
  reliably grounded, and it refuses to fabricate when the sources don't support
  an answer. That trustworthiness is the core value, so it stays.
- **The router → retrieve → tool → cite loop.** Router accuracy of 0.95 shows the
  agent escalates to web search at the right times. Keeping a corpus-first, web-
  fallback design keeps answers grounded by default while still handling current
  questions.
- **The multi-agent PRD pipeline with a human-approval step.** Intake → research
  → writer → critic → revision → tickets, with a review-and-approve gate, is a
  strong demonstration of orchestration and human-in-the-loop, and it works end
  to end in production.
- **The production stack:** Next.js + FastAPI on Vercel, Clerk auth, Qdrant Cloud,
  the Helicone gateway (which doubles as monitoring), and per-step observability.
  It deploys cleanly and runs in a browser on phone and laptop.
- **The evaluation harness.** Being able to measure retrieval, routing, and answer
  quality against a gold set is what made every improvement decision data-driven,
  so it stays as a first-class part of the project.

## What I'd change or improve

- **Retrieval precision (highest priority).** The baseline exposed context
  precision of 0.63 — a third of retrieved context is noise. The Task 6
  retrieve-then-rerank retriever addresses this; I'd make reranking the default
  once the after-numbers confirm the gain, and explore hybrid (BM25 + dense)
  retrieval for robustness.
- **PRD-pipeline latency.** The full pipeline can approach the serverless time
  limit. I'd parallelize independent steps, make the revision pass conditional on
  severity, and stream partial output so the user sees progress.
- **Richer web answers.** The web-search answers were a touch over-cautious; I'd
  use Tavily's advanced depth / answer synthesis and a slightly less hesitant
  synthesis prompt so escalated answers are more complete.
- **Streaming and UX polish.** Stream FAQ answers token-by-token, and add explicit
  "✓ saved" feedback on the PRD approval step (currently silent).
- **Production auth and a larger corpus.** Move Clerk from development to a
  production instance, and expand the knowledge base with the user's own PRDs and
  PM playbooks so answers reflect their organization's practices.
- **Feedback capture.** Add thumbs-up/down on answers to build a real evaluation
  set from live usage and close the loop back into the eval harness.

## Reasoning

The theme is: keep everything that the evaluation proved is working and
trustworthy, and direct effort at the one place the data says there's headroom
(retrieval precision) plus the two things a live audience will feel most
(latency and streaming). Because the eval harness is in place, each of these
changes can be justified with before/after numbers rather than intuition.
