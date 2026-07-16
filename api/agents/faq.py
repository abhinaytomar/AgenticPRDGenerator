"""FAQ agent: Agentic RAG over the PM/PRD corpus + Tavily web search.

Flow (agentic decision point):
  1. Retrieve the top-k passages from the Qdrant corpus (RAG).
  2. A router LLM decides whether the corpus is enough or a web search is
     also needed. This is the agent's reasoning/decision step.
  3. If needed, call the Tavily tool for public results.
  4. Synthesize a grounded, cited answer from the assembled context.
Conversation history is threaded through as a lightweight memory component.
"""

from __future__ import annotations

import json

from api.llm import chat_completion
from api.models import ChatTurn, Citation, FAQResponse
from api.prompts import (
    FAQ_ROUTER_SYSTEM,
    FAQ_ROUTER_USER,
    FAQ_ANSWER_SYSTEM,
    FAQ_ANSWER_USER,
    format_history_block,
)
from api.observability import StepTracker
from api.rag.retriever import retrieve
from api.tools.tavily import tavily_search, tavily_available

CORPUS_TOP_K = 5
WEB_MAX_RESULTS = 4


def _router_decision(question: str, corpus_previews: str, tracker: StepTracker) -> tuple[bool, str]:
    """Ask the LLM whether a web search is warranted in addition to the corpus."""
    if not tavily_available():
        return False, "Web search not configured; using local knowledge base only."

    user_msg = FAQ_ROUTER_USER.format(question=question, corpus_previews=corpus_previews)
    with tracker.track_step("faq_router") as trace:
        resp = chat_completion(
            messages=[
                {"role": "system", "content": FAQ_ROUTER_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
        )
        usage = resp.usage
        if usage:
            trace["input_tokens"] = usage.prompt_tokens
            trace["output_tokens"] = usage.completion_tokens

    try:
        raw = json.loads(resp.choices[0].message.content)
        return bool(raw.get("use_web", False)), str(raw.get("reason", ""))
    except (json.JSONDecodeError, TypeError):
        return False, "Router response could not be parsed; defaulting to corpus only."


def run_faq(question: str, history: list[ChatTurn], tracker: StepTracker) -> FAQResponse:
    # ── Step 1: RAG retrieval ──────────────────────────────────────────────
    with tracker.track_step("faq_retrieve"):
        corpus_hits = retrieve(question, top_k=CORPUS_TOP_K)

    corpus_previews = "\n".join(
        f"- ({h.title} > {h.heading}) {h.text[:160]}..." for h in corpus_hits
    ) or "No local passages retrieved."

    # ── Step 2: agentic routing decision ───────────────────────────────────
    use_web, reason = _router_decision(question, corpus_previews, tracker)

    # ── Step 3: optional web search tool ───────────────────────────────────
    web_hits = []
    if use_web:
        with tracker.track_step("faq_web_search"):
            web_hits = tavily_search(question, max_results=WEB_MAX_RESULTS)
        if not web_hits:
            reason += " (web search returned no usable results)"

    # ── Build numbered context + citations ─────────────────────────────────
    context_blocks: list[str] = []
    citations: list[Citation] = []
    n = 0
    for h in corpus_hits:
        n += 1
        label = f"{h.title} — {h.heading}".strip(" —")
        context_blocks.append(f"[{n}] (knowledge base: {label})\n{h.text}")
        citations.append(
            Citation(
                n=n, kind="corpus", title=h.title or h.source, source=h.source,
                heading=h.heading, score=round(h.score, 4), snippet=h.text[:200],
            )
        )
    for w in web_hits:
        n += 1
        context_blocks.append(f"[{n}] (web: {w.title} — {w.url})\n{w.content}")
        citations.append(
            Citation(
                n=n, kind="web", title=w.title or w.url, source=w.url,
                score=round(w.score, 4), snippet=w.content[:200],
            )
        )

    context_block = "\n\n".join(context_blocks) or "No context available."
    history_block = format_history_block([t.model_dump() for t in history])

    # ── Step 4: grounded, cited synthesis ──────────────────────────────────
    user_msg = FAQ_ANSWER_USER.format(
        history_block=history_block, question=question, context_block=context_block,
    )
    with tracker.track_step("faq_answer") as trace:
        resp = chat_completion(
            messages=[
                {"role": "system", "content": FAQ_ANSWER_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
        )
        usage = resp.usage
        if usage:
            trace["input_tokens"] = usage.prompt_tokens
            trace["output_tokens"] = usage.completion_tokens

    answer = resp.choices[0].message.content or ""

    return FAQResponse(
        answer=answer,
        citations=citations,
        used_web=bool(web_hits),
        route_reason=reason,
        meta=tracker.build_meta(),
    )
