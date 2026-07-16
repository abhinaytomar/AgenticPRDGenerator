# PRD Generator FAQ — Evaluation Report

Test set: **21 questions** · retrieval top-k = **5**

## Aggregate metrics

| Metric | Score | Notes |
|---|---|---|
| Retrieval Hit@5 | 1.00 | expected doc in top-5 (18 KB questions) |
| Retrieval Hit@3 | 1.00 | expected doc in top-3 |
| Retrieval MRR | 1.00 | mean reciprocal rank of the expected doc |
| Context precision | 0.63 | fraction of retrieved chunks from the expected doc |
| Router accuracy | 0.95 | correct web-vs-corpus decision (all questions) |
| Answer correctness | 0.94 | LLM-judge vs reference (18 KB questions) |
| Answer faithfulness | 0.94 | LLM-judge, grounded in context |
| Answer relevancy | 0.94 | LLM-judge, addresses the question |

## Per-question detail

| ID | Category | Hit@k | RR | Router ✓ | Correct | Faithful | Relevant |
|---|---|---|---|---|---|---|---|
| kb-01 | concept | ✅ | 1.00 | ✅ | 5 | 5 | 5 |
| kb-02 | concept | ✅ | 1.00 | ✅ | 5 | 5 | 5 |
| kb-03 | concept | ✅ | 1.00 | ✅ | 5 | 5 | 5 |
| kb-04 | concept | ✅ | 1.00 | ✅ | 4 | 4 | 4 |
| kb-05 | framework | ✅ | 1.00 | ✅ | 5 | 5 | 5 |
| kb-06 | framework | ✅ | 1.00 | ✅ | 4 | 4 | 4 |
| kb-07 | framework | ✅ | 1.00 | ✅ | 5 | 5 | 5 |
| kb-08 | concept | ✅ | 1.00 | ✅ | 4 | 4 | 4 |
| kb-09 | framework | ✅ | 1.00 | ✅ | 5 | 5 | 5 |
| kb-10 | framework | ✅ | 1.00 | ✅ | 5 | 5 | 5 |
| kb-11 | concept | ✅ | 1.00 | ✅ | 5 | 5 | 5 |
| kb-12 | framework | ✅ | 1.00 | ✅ | 4 | 4 | 4 |
| kb-13 | framework | ✅ | 1.00 | ✅ | 4 | 4 | 4 |
| kb-14 | concept | ✅ | 1.00 | ✅ | 5 | 5 | 5 |
| kb-15 | concept | ✅ | 1.00 | ✅ | 5 | 5 | 5 |
| kb-16 | framework | ✅ | 1.00 | ✅ | 5 | 5 | 5 |
| kb-17 | framework | ✅ | 1.00 | ✅ | 5 | 5 | 5 |
| kb-18 | concept | ✅ | 1.00 | ✅ | 5 | 5 | 5 |
| web-01 | web | — | — | ✅ | — | — | — |
| web-02 | web | — | — | ✅ | — | — | — |
| oos-01 | out_of_scope | — | — | ❌ | — | — | — |

_Scores from LLM-as-judge are 1–5. Retrieval metrics are deterministic against the expected source document(s)._