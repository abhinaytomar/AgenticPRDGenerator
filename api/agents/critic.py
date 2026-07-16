"""Critic agent: evaluates PRD quality and readiness."""

from __future__ import annotations

import json

from api.llm import chat_completion

from api.models import PRDDocument, CriticEvaluation
from api.prompts import CRITIC_SYSTEM, CRITIC_USER
from api.observability import StepTracker


def run_critic(prd: PRDDocument, tracker: StepTracker) -> CriticEvaluation:

    prd_json = prd.model_dump_json(indent=2)
    user_msg = CRITIC_USER.format(prd_json=prd_json)

    with tracker.track_step("critic") as trace:
        response = chat_completion(
            messages=[
                {"role": "system", "content": CRITIC_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
        )

        usage = response.usage
        if usage:
            trace["input_tokens"] = usage.prompt_tokens
            trace["output_tokens"] = usage.completion_tokens

    raw = json.loads(response.choices[0].message.content)
    return CriticEvaluation(**raw)
