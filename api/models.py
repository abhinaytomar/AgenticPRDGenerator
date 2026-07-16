"""Pydantic models for all API request/response schemas."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, field_validator  # type: ignore


# ── LLM output coercion helpers ────────────────────────────────────────────
# LLMs (esp. smaller models) sometimes return richer objects than a schema
# expects — e.g. a list of {"metric": ..., "cadence": ...} dicts where we asked
# for a list of strings. Rather than 500 on a type mismatch, coerce gracefully.

def _stringify(item) -> str:
    """Turn a single list item into a readable string."""
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        # Lead with a primary field if present, then append the rest.
        primary_keys = ("metric", "question", "name", "title", "description", "text", "goal")
        lead = next((str(item[k]) for k in primary_keys if item.get(k)), None)
        extras = [f"{k}: {v}" for k, v in item.items()
                  if not (lead and str(v) == lead) and v not in (None, "", [])]
        if lead:
            tail = "; ".join(e for e in extras if not e.startswith(tuple(f"{k}:" for k in primary_keys)))
            return f"{lead}" + (f" ({tail})" if tail else "")
        return " | ".join(f"{k}: {v}" for k, v in item.items())
    return str(item)


def _coerce_str_list(v):
    """Coerce a value into a list[str], stringifying any non-string items."""
    if v is None:
        return []
    if isinstance(v, str):
        return [v]
    if isinstance(v, list):
        return [_stringify(x) for x in v]
    return [str(v)]


# ── Shared / Meta ──────────────────────────────────────────────────────────

class StepMeta(BaseModel):
    """Observability metadata attached to every API response."""
    request_id: str
    steps: list[StepTrace] = []
    total_latency_ms: float = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0


class StepTrace(BaseModel):
    step: str
    latency_ms: float
    tokens: int
    estimated_cost_usd: float
    success: bool


# ── Intake ─────────────────────────────────────────────────────────────────

class IntakeRequest(BaseModel):
    product_name: str
    problem_statement: str
    context: str = ""


class ClarifyingQuestion(BaseModel):
    id: str
    question: str
    rationale: str
    example_answer: str


class IntakeResponse(BaseModel):
    questions: list[ClarifyingQuestion]
    meta: StepMeta


# ── Generate (orchestrates research → write → critic → revision) ──────────

class QuestionAnswer(BaseModel):
    question_id: str
    question: str
    answer: str


class GenerateRequest(BaseModel):
    intake: IntakeRequest
    answers: list[QuestionAnswer]


# ── PRD Document (structured) ─────────────────────────────────────────────

class FunctionalRequirement(BaseModel):
    id: str = ""
    title: str = ""
    description: str = ""
    acceptance_criteria: list[str] = []
    priority: str = "must-have"

    _coerce_ac = field_validator("acceptance_criteria", mode="before")(_coerce_str_list)


class NonFunctionalRequirement(BaseModel):
    id: str = ""
    category: str = ""
    description: str = ""
    metric: str = ""


class UserFlow(BaseModel):
    name: str = ""
    steps: list[str] = []
    error_scenarios: list[str] = []

    _coerce_lists = field_validator("steps", "error_scenarios", mode="before")(_coerce_str_list)


class Risk(BaseModel):
    description: str = ""
    severity: str = ""
    mitigation: str = ""


class PRDDocument(BaseModel):
    title: str = ""
    summary: str = ""
    problem_statement: str = ""
    target_users: list[str] = []
    goals: list[str] = []
    non_goals: list[str] = []
    assumptions: list[str] = []
    functional_requirements: list[FunctionalRequirement] = []
    non_functional_requirements: list[NonFunctionalRequirement] = []
    user_flows: list[UserFlow] = []
    success_metrics: list[str] = []
    risks: list[Risk] = []
    open_questions: list[str] = []
    dependencies: list[str] = []
    release_considerations: list[str] = []

    _coerce_str_lists = field_validator(
        "target_users", "goals", "non_goals", "assumptions",
        "success_metrics", "open_questions", "dependencies", "release_considerations",
        mode="before",
    )(_coerce_str_list)


# ── Critic ─────────────────────────────────────────────────────────────────

class CriticIssue(BaseModel):
    category: str
    severity: str  # "critical" | "major" | "minor"
    location: str
    suggestion: str


class CriticEvaluation(BaseModel):
    quality_score: int = 0
    confidence_score: int = 0
    issues: list[CriticIssue] = []
    recommendations: list[str] = []
    readiness: str = "needs_revision"  # "ready" | "needs_revision" | "major_rework"

    _coerce_recs = field_validator("recommendations", mode="before")(_coerce_str_list)

    @field_validator("quality_score", "confidence_score", mode="before")
    @classmethod
    def _clamp_score(cls, v):
        try:
            return max(0, min(100, int(round(float(v)))))
        except (TypeError, ValueError):
            return 0


# ── Generate response ─────────────────────────────────────────────────────

class GenerateResponse(BaseModel):
    prd: PRDDocument
    evaluation: CriticEvaluation
    revision_applied: bool
    prd_markdown: str
    meta: StepMeta


# ── Research (internal) ───────────────────────────────────────────────────

class ResearchContext(BaseModel):
    market_analysis: str = ""
    target_audience_insights: str = ""
    technical_considerations: str = ""
    competitive_landscape: str = ""
    key_risks: list[str] = []

    _coerce_risks = field_validator("key_risks", mode="before")(_coerce_str_list)


# ── Tickets ────────────────────────────────────────────────────────────────

class AcceptanceCriterion(BaseModel):
    given: str
    when: str
    then: str


class Story(BaseModel):
    id: str
    title: str
    description: str
    acceptance_criteria: list[AcceptanceCriterion]
    story_points: int = 0


class Epic(BaseModel):
    id: str
    title: str
    description: str
    stories: list[Story]


class TicketsRequest(BaseModel):
    prd: PRDDocument


class TicketsResponse(BaseModel):
    epics: list[Epic]
    total_story_count: int
    meta: StepMeta


# ── FAQ (Agentic RAG) ──────────────────────────────────────────────────────

class ChatTurn(BaseModel):
    """A single prior turn in the FAQ conversation (memory component)."""
    role: str  # "user" | "assistant"
    content: str


class FAQRequest(BaseModel):
    question: str
    history: list[ChatTurn] = []


class Citation(BaseModel):
    n: int                       # citation number referenced in the answer, e.g. [1]
    kind: str                    # "corpus" | "web"
    title: str
    source: str                  # filename for corpus, URL for web
    heading: str = ""
    score: float = 0.0
    snippet: str = ""


class FAQResponse(BaseModel):
    answer: str
    citations: list[Citation]
    used_web: bool
    route_reason: str = ""
    meta: StepMeta
