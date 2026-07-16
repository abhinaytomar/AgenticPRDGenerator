"""Writer agent: produces structured PRD JSON. Also handles revisions."""

from __future__ import annotations

import json

from api.llm import chat_completion

from api.models import (
    IntakeRequest,
    QuestionAnswer,
    ResearchContext,
    PRDDocument,
    CriticEvaluation,
)
from api.prompts import (
    WRITER_SYSTEM,
    WRITER_USER,
    REVISION_SYSTEM,
    REVISION_USER,
    format_qa_block,
)
from api.observability import StepTracker


def run_writer(
    intake: IntakeRequest,
    answers: list[QuestionAnswer],
    research: ResearchContext,
    tracker: StepTracker,
) -> PRDDocument:

    qa_block = format_qa_block([a.model_dump() for a in answers])

    research_text = (
        f"Market Analysis: {research.market_analysis}\n"
        f"Target Audience: {research.target_audience_insights}\n"
        f"Technical Considerations: {research.technical_considerations}\n"
        f"Competitive Landscape: {research.competitive_landscape}\n"
        f"Key Risks: {', '.join(research.key_risks)}"
    )

    user_msg = WRITER_USER.format(
        product_name=intake.product_name,
        problem_statement=intake.problem_statement,
        context=intake.context or "None provided",
        qa_block=qa_block,
        research_context=research_text,
    )

    with tracker.track_step("writer") as trace:
        response = chat_completion(
            messages=[
                {"role": "system", "content": WRITER_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
        )

        usage = response.usage
        if usage:
            trace["input_tokens"] = usage.prompt_tokens
            trace["output_tokens"] = usage.completion_tokens

    raw = json.loads(response.choices[0].message.content)
    return PRDDocument(**raw)


def run_revision(
    prd: PRDDocument,
    evaluation: CriticEvaluation,
    tracker: StepTracker,
) -> PRDDocument:

    prd_json = prd.model_dump_json(indent=2)
    issues_block = "\n".join(
        f"- [{i.severity}] {i.category} in '{i.location}': {i.suggestion}"
        for i in evaluation.issues
    )
    recommendations_block = "\n".join(f"- {r}" for r in evaluation.recommendations)

    user_msg = REVISION_USER.format(
        prd_json=prd_json,
        issues_block=issues_block or "No specific issues.",
        recommendations_block=recommendations_block or "No specific recommendations.",
    )

    with tracker.track_step("revision") as trace:
        response = chat_completion(
            messages=[
                {"role": "system", "content": REVISION_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
        )

        usage = response.usage
        if usage:
            trace["input_tokens"] = usage.prompt_tokens
            trace["output_tokens"] = usage.completion_tokens

    raw = json.loads(response.choices[0].message.content)
    return PRDDocument(**raw)
