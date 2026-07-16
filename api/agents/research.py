"""Research agent: synthesizes structured context from product idea and Q&A."""

from __future__ import annotations

import json

from api.llm import chat_completion

from api.models import IntakeRequest, QuestionAnswer, ResearchContext
from api.prompts import RESEARCH_SYSTEM, RESEARCH_USER, format_qa_block
from api.observability import StepTracker


def run_research(
    intake: IntakeRequest,
    answers: list[QuestionAnswer],
    tracker: StepTracker,
) -> ResearchContext:

    qa_block = format_qa_block([a.model_dump() for a in answers])

    user_msg = RESEARCH_USER.format(
        product_name=intake.product_name,
        problem_statement=intake.problem_statement,
        context=intake.context or "None provided",
        qa_block=qa_block,
    )

    with tracker.track_step("research") as trace:
        response = chat_completion(
            messages=[
                {"role": "system", "content": RESEARCH_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
        )

        usage = response.usage
        if usage:
            trace["input_tokens"] = usage.prompt_tokens
            trace["output_tokens"] = usage.completion_tokens

    raw = json.loads(response.choices[0].message.content)
    return ResearchContext(**raw)
