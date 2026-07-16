"""Evaluation harness for the PRD Generator FAQ (Agentic RAG).

Measures three things against the gold set in eval/testset.json:

  1. Retrieval quality  — Hit@k and MRR: did the expected corpus document
     appear in the top-k retrieved chunks? (deterministic, no LLM)
  2. Router accuracy    — did the agent correctly decide whether to escalate
     to web search? (agent-specific eval)
  3. Answer quality     — LLM-as-judge scores for correctness (vs the reference
     answer), faithfulness (grounded in retrieved context), and relevancy.

Optionally also runs RAGAS (see eval/ragas_eval.py) with `--ragas`.

Run from the repo root (needs the same .env.local as the app):

    python -m eval.run_eval
    python -m eval.run_eval --ragas          # also run RAGAS metrics
    python -m eval.run_eval --top-k 5

Outputs eval/results.json and eval/report.md.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from dotenv import load_dotenv  # type: ignore

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(_ROOT, ".env.local"))

from api.llm import chat_completion  # noqa: E402
from api.rag.retriever import retrieve  # noqa: E402
from api.prompts import FAQ_ANSWER_SYSTEM, FAQ_ANSWER_USER  # noqa: E402

TOP_K = 5

JUDGE_SYSTEM = """You are a strict evaluation judge for a product-management FAQ assistant.
You are given a user question, a reference (gold) answer, the context passages the
assistant retrieved, and the assistant's answer. Score the assistant's answer on three
dimensions from 1 (worst) to 5 (best):

- correctness: does the answer agree with the reference answer and correctly address the question?
- faithfulness: is every claim supported by the retrieved context (no hallucination)?
- relevancy: does the answer directly address the question without padding or drift?

Return valid JSON only:
{"correctness": 1-5, "faithfulness": 1-5, "relevancy": 1-5, "rationale": "one sentence"}"""

JUDGE_USER = """Question:
{question}

Reference answer:
{ground_truth}

Retrieved context:
{context}

Assistant answer:
{answer}

Score the assistant answer."""

ROUTER_JUDGE_SYSTEM = """You decide whether answering a product-management question well
requires a live web search (current events, specific vendors/tools, pricing, recent
releases) versus timeless PM knowledge. Return valid JSON only:
{"use_web": true or false}"""


def _context_block(chunks: list[str]) -> str:
    return "\n\n".join(f"[{i + 1}] {c}" for i, c in enumerate(chunks)) or "No context."


def answer_from_contexts(question: str, contexts: list[str]) -> str:
    """Generate an answer grounded in the retrieved contexts (mirrors the FAQ agent)."""
    user_msg = FAQ_ANSWER_USER.format(
        history_block="", question=question, context_block=_context_block(contexts)
    )
    resp = chat_completion(
        messages=[
            {"role": "system", "content": FAQ_ANSWER_SYSTEM},
            {"role": "user", "content": user_msg},
        ]
    )
    return resp.choices[0].message.content or ""


def route_decision(question: str, contexts: list[str]) -> bool:
    """Ask the model whether the question needs web search (mirrors the router)."""
    previews = "\n".join(f"- {c[:160]}" for c in contexts) or "No local passages."
    resp = chat_completion(
        messages=[
            {"role": "system", "content": ROUTER_JUDGE_SYSTEM},
            {"role": "user", "content": f"Question: {question}\n\nLocal passages:\n{previews}"},
        ],
        response_format={"type": "json_object"},
    )
    try:
        return bool(json.loads(resp.choices[0].message.content).get("use_web", False))
    except (json.JSONDecodeError, TypeError, AttributeError):
        return False


def judge_answer(question: str, ground_truth: str, contexts: list[str], answer: str) -> dict:
    resp = chat_completion(
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": JUDGE_USER.format(
                question=question, ground_truth=ground_truth,
                context=_context_block(contexts), answer=answer)},
        ],
        response_format={"type": "json_object"},
    )
    try:
        raw = json.loads(resp.choices[0].message.content)
        return {
            "correctness": int(raw.get("correctness", 0)),
            "faithfulness": int(raw.get("faithfulness", 0)),
            "relevancy": int(raw.get("relevancy", 0)),
            "rationale": str(raw.get("rationale", "")),
        }
    except (json.JSONDecodeError, TypeError, ValueError):
        return {"correctness": 0, "faithfulness": 0, "relevancy": 0, "rationale": "unparseable"}


def retrieval_metrics(retrieved_sources: list[str], expected: list[str], k: int) -> dict:
    """Hit@k and reciprocal rank against the expected source document(s)."""
    exp = set(expected)
    top = retrieved_sources[:k]
    hit_k = any(s in exp for s in top)
    hit_3 = any(s in exp for s in retrieved_sources[:3])
    rr = 0.0
    for rank, s in enumerate(retrieved_sources, start=1):
        if s in exp:
            rr = 1.0 / rank
            break
    precision = sum(1 for s in top if s in exp) / len(top) if top else 0.0
    return {"hit@k": hit_k, "hit@3": hit_3, "reciprocal_rank": rr, "context_precision": precision}


def _mean(xs: list[float]) -> float:
    return round(sum(xs) / len(xs), 3) if xs else 0.0


def run(top_k: int, with_ragas: bool) -> None:
    testset = json.load(open(os.path.join(_ROOT, "eval", "testset.json"), encoding="utf-8"))
    items = testset["items"]

    rows: list[dict] = []
    ragas_samples: list[dict] = []

    for it in items:
        q = it["question"]
        print(f"  [{it['id']}] {q[:60]}...")
        row: dict = {"id": it["id"], "question": q, "category": it["category"]}
        try:
            retrieved = retrieve(q, top_k=top_k)
            sources = [r.source for r in retrieved]
            contexts = [r.text for r in retrieved]
            row["retrieved_sources"] = sources

            # Router accuracy (all items)
            use_web = route_decision(q, contexts)
            row["router_use_web"] = use_web
            row["router_expected"] = it["expects_web"]
            row["router_correct"] = (use_web == it["expects_web"])

            # Retrieval metrics (only where we expect a specific corpus doc)
            if it.get("expected_sources"):
                row["retrieval"] = retrieval_metrics(sources, it["expected_sources"], top_k)

            # Answer quality (knowledge-base questions only)
            if not it["expects_web"]:
                answer = answer_from_contexts(q, contexts)
                row["answer"] = answer
                row["judge"] = judge_answer(q, it["ground_truth"], contexts, answer)
                ragas_samples.append({
                    "question": q, "answer": answer, "contexts": contexts,
                    "ground_truth": it["ground_truth"],
                })
        except Exception as exc:  # noqa: BLE001
            row["error"] = str(exc)
            print(f"    ERROR: {exc}")
        rows.append(row)

    # ── Aggregate ──────────────────────────────────────────────────────────
    kb_rows = [r for r in rows if r.get("retrieval")]
    judged = [r for r in rows if r.get("judge")]
    summary = {
        "n_items": len(rows),
        "retrieval": {
            "hit@k": _mean([1.0 if r["retrieval"]["hit@k"] else 0.0 for r in kb_rows]),
            "hit@3": _mean([1.0 if r["retrieval"]["hit@3"] else 0.0 for r in kb_rows]),
            "mrr": _mean([r["retrieval"]["reciprocal_rank"] for r in kb_rows]),
            "context_precision": _mean([r["retrieval"]["context_precision"] for r in kb_rows]),
            "n": len(kb_rows),
        },
        "router_accuracy": _mean([1.0 if r.get("router_correct") else 0.0 for r in rows if "router_correct" in r]),
        "answer_quality": {
            "correctness": _mean([r["judge"]["correctness"] / 5 for r in judged]),
            "faithfulness": _mean([r["judge"]["faithfulness"] / 5 for r in judged]),
            "relevancy": _mean([r["judge"]["relevancy"] / 5 for r in judged]),
            "n": len(judged),
        },
        "top_k": top_k,
    }

    ragas_scores = None
    if with_ragas:
        try:
            from eval.ragas_eval import run_ragas
            ragas_scores = run_ragas(ragas_samples)
            summary["ragas"] = ragas_scores
        except Exception as exc:  # noqa: BLE001
            print(f"RAGAS step failed ({exc}); skipping. See eval/ragas_eval.py.")
            summary["ragas_error"] = str(exc)

    results = {"summary": summary, "rows": rows}
    with open(os.path.join(_ROOT, "eval", "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    _write_report(summary, rows)
    print("\nDone. Wrote eval/results.json and eval/report.md")
    print(json.dumps(summary, indent=2))


def _write_report(summary: dict, rows: list[dict]) -> None:
    L: list[str] = []
    L.append("# PRD Generator FAQ — Evaluation Report\n")
    L.append(f"Test set: **{summary['n_items']} questions** · retrieval top-k = **{summary['top_k']}**\n")

    L.append("## Aggregate metrics\n")
    r = summary["retrieval"]
    L.append("| Metric | Score | Notes |")
    L.append("|---|---|---|")
    L.append(f"| Retrieval Hit@{summary['top_k']} | {r['hit@k']:.2f} | expected doc in top-{summary['top_k']} ({r['n']} KB questions) |")
    L.append(f"| Retrieval Hit@3 | {r['hit@3']:.2f} | expected doc in top-3 |")
    L.append(f"| Retrieval MRR | {r['mrr']:.2f} | mean reciprocal rank of the expected doc |")
    L.append(f"| Context precision | {r['context_precision']:.2f} | fraction of retrieved chunks from the expected doc |")
    L.append(f"| Router accuracy | {summary['router_accuracy']:.2f} | correct web-vs-corpus decision (all questions) |")
    a = summary["answer_quality"]
    L.append(f"| Answer correctness | {a['correctness']:.2f} | LLM-judge vs reference ({a['n']} KB questions) |")
    L.append(f"| Answer faithfulness | {a['faithfulness']:.2f} | LLM-judge, grounded in context |")
    L.append(f"| Answer relevancy | {a['relevancy']:.2f} | LLM-judge, addresses the question |")
    if summary.get("ragas"):
        for k, v in summary["ragas"].items():
            L.append(f"| RAGAS {k} | {v:.2f} | ragas library |")
    L.append("")

    L.append("## Per-question detail\n")
    L.append("| ID | Category | Hit@k | RR | Router ✓ | Correct | Faithful | Relevant |")
    L.append("|---|---|---|---|---|---|---|---|")
    for row in rows:
        ret = row.get("retrieval", {})
        j = row.get("judge", {})
        hit = "✅" if ret.get("hit@k") else ("❌" if ret else "—")
        rr = f"{ret.get('reciprocal_rank', 0):.2f}" if ret else "—"
        router = "✅" if row.get("router_correct") else ("❌" if "router_correct" in row else "—")
        cor = j.get("correctness", "—")
        fai = j.get("faithfulness", "—")
        rel = j.get("relevancy", "—")
        L.append(f"| {row['id']} | {row['category']} | {hit} | {rr} | {router} | {cor} | {fai} | {rel} |")
    L.append("")
    L.append("_Scores from LLM-as-judge are 1–5. Retrieval metrics are deterministic against the expected source document(s)._")

    with open(os.path.join(_ROOT, "eval", "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def main() -> None:
    p = argparse.ArgumentParser(description="Evaluate the FAQ Agentic RAG pipeline.")
    p.add_argument("--top-k", type=int, default=TOP_K)
    p.add_argument("--ragas", action="store_true", help="also run RAGAS metrics")
    args = p.parse_args()
    run(args.top_k, args.ragas)


if __name__ == "__main__":
    main()
