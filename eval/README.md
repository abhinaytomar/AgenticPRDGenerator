# Evaluation Harness — PRD Generator FAQ (Agentic RAG)

This harness baselines the FAQ retrieval-augmented pipeline against a gold test
set. It is the Task 5 deliverable and produces the "before" numbers for the
Task 6 improvements.

## What it measures

| Dimension | Metric | Method |
|---|---|---|
| **Retrieval** | Hit@k, Hit@3, MRR, context precision | Deterministic — checks whether the expected corpus document is in the top-k retrieved chunks (no LLM, fully reproducible). |
| **Router (agent)** | Accuracy | Does the agent correctly decide web-search vs. corpus for each question? |
| **Answer quality** | Correctness, faithfulness, relevancy | Prompted **LLM-as-judge** (1–5) against the reference answer and retrieved context. |
| **RAGAS (optional)** | faithfulness, response relevancy, context precision/recall | The RAGAS library (`--ragas`). |

## Test set

`eval/testset.json` — 21 questions: 18 knowledge-base questions (each with a
reference answer and the expected source document), 2 that should trigger web
search, and 1 out-of-scope question. Edit or extend it freely.

## Run it

From the repo root, with the same `.env.local` the app uses (needs
`OPENAI_API_KEY`/`HELICONE_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`; the Qdrant
collection must already be ingested):

```bash
# Core harness (retrieval + router + LLM-as-judge)
python -m eval.run_eval

# Also run RAGAS (install extra deps first)
pip install -r eval/requirements-eval.txt
python -m eval.run_eval --ragas

# Change retrieval depth
python -m eval.run_eval --top-k 5
```

## Outputs

- `eval/results.json` — full per-question results (retrieved sources, answers, judge scores).
- `eval/report.md` — aggregate metrics table + per-question table (paste into the submission).

## Notes

- The core harness has **no extra dependencies** beyond the app. RAGAS is
  optional and version-sensitive; if `--ragas` errors, the core report is still
  produced.
- LLM calls route through the same Helicone gateway as the app, so eval runs are
  visible in the monitoring dashboard too.
