# Task 5 — Evaluation: Baselining the FAQ Agentic RAG

## Test data set

A gold set of **21 questions** (`eval/testset.json`) covering the questions a
target user is likely to ask: 18 knowledge-base questions — each with a written
reference answer and the specific corpus document that should be retrieved — 2
questions that require current public information (should trigger web search),
and 1 out-of-scope question. The set spans every document in the corpus and both
"concept" and "framework" question types.

## Evaluation harness

The harness (`eval/run_eval.py`) scores three dimensions plus an optional RAGAS
pass, so it evaluates the RAG **and** the agent behavior:

- **Retrieval quality (deterministic):** Hit@k, Hit@3, MRR, and context
  precision, computed by checking whether the expected source document appears
  in the top-k retrieved chunks. No LLM is involved, so these numbers are exact
  and reproducible.
- **Router accuracy (agent-specific):** for every question, does the agent
  correctly decide whether to answer from the corpus or escalate to web search?
- **Answer quality (LLM-as-judge):** a prompted judge scores each answer 1–5 for
  correctness (vs. the reference), faithfulness (grounded in retrieved context),
  and relevancy.
- **RAGAS (optional):** faithfulness, response relevancy, context precision, and
  context recall via the RAGAS library (`--ragas`).

All judge/router calls route through the same Helicone gateway as the app, so
evaluation runs are observable alongside production traffic.

## Baseline results

Retrieval top-k = 5, model = `gpt-5-nano` (minimal reasoning).

| Metric | Score | Interpretation |
|---|---|---|
| Retrieval Hit@5 | **1.00** | the correct document is always in the top 5 |
| Retrieval Hit@3 | **1.00** | …and always in the top 3 |
| Retrieval MRR | **1.00** | …and always ranked **first** |
| Context precision | **0.63** | only ~63% of retrieved chunks are from the right document |
| Router accuracy | **0.95** | 20/21 web-vs-corpus decisions correct |
| Answer correctness | **0.94** | LLM-judge vs. reference answer |
| Answer faithfulness | **0.94** | LLM-judge, grounded in context |
| Answer relevancy | **0.94** | LLM-judge, addresses the question |

*(Full per-question table in `eval/report.md`.)*

## What we can conclude

**Retrieval recall is already excellent — precision is the bottleneck.** With
Hit@k and MRR both at 1.00, the dense-embedding retriever reliably finds the
correct document and ranks its best chunk first. But context precision of 0.63
means roughly a third of the context passed to the answer model comes from
*other* documents. That off-topic context is the direct cause of the qualitative
issue observed earlier (the "what sections should a PRD contain?" answer leaning
on a tangential "keep it skimmable" chunk) and correlates with the five answers
that scored 4 rather than 5. **The single highest-leverage improvement is to
raise context precision** — i.e., feed the answer model fewer, cleaner chunks.

**Answer quality is high but capped by that noise.** 0.94 across all three
answer dimensions is strong, and faithfulness at 0.94 confirms the system
grounds its claims and rarely hallucinates (consistent with its willingness to
refuse when unsupported). The gap to 1.00 is concentrated on questions whose
retrieved context was diluted — so improving retrieval precision should also
lift answer correctness.

**The agent's routing is reliable.** 0.95 router accuracy shows the agent
escalates to web search at the right times: it correctly kept knowledge-base
questions local and sent the two current-information questions to Tavily. The
single "miss" is the out-of-scope weather question, where the router chose *not*
to search — arguably the safer behavior for an out-of-scope query, so this is
closer to a test-labeling nuance than a real defect, but it's worth refining.

**Implication for Task 6.** The baseline isolates a concrete, measurable target:
context precision (0.63). The Task 6 hypothesis is that adding an **advanced
retriever that reranks a larger candidate set down to the most relevant few
chunks** will raise context precision, which should in turn lift answer
correctness on the borderline questions — with recall already at 1.00, there is
no recall to trade away.
