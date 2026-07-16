"""Intake agent: generates clarifying questions from a product idea."""

from __future__ import annotations

import json

from api.llm import chat_completion

from api.models import IntakeRequest, IntakeResponse, ClarifyingQuestion, StepMeta
from api.prompts import INTAKE_SYSTEM, INTAKE_USER
from api.observability import StepTracker


def run_intake(request: IntakeRequest, tracker: StepTracker) -> IntakeResponse:

    user_msg = INTAKE_USER.format(
        product_name=request.product_name,
        problem_statement=request.problem_statement,
        context=request.context or "None provided",
    )

    with tracker.track_step("intake") as trace:
        response = chat_completion(
            messages=[
                {"role": "system", "content": INTAKE_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
        )

        usage = response.usage
        if usage:
            trace["input_tokens"] = usage.prompt_tokens
            trace["output_tokens"] = usage.completion_tokens

    raw = json.loads(response.choices[0].message.content)
    questions = [ClarifyingQuestion(**q) for q in raw["questions"]]

    return IntakeResponse(
        questions=questions,
        meta=tracker.build_meta(),
    )
