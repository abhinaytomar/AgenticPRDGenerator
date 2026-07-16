"""Ticket generator agent: creates epics and stories from a PRD."""

from __future__ import annotations

import json

from api.llm import chat_completion

from api.models import PRDDocument, TicketsResponse, Epic
from api.prompts import TICKETS_SYSTEM, TICKETS_USER
from api.observability import StepTracker


def run_tickets(prd: PRDDocument, tracker: StepTracker) -> TicketsResponse:

    prd_json = prd.model_dump_json(indent=2)
    user_msg = TICKETS_USER.format(prd_json=prd_json)

    with tracker.track_step("tickets") as trace:
        response = chat_completion(
            messages=[
                {"role": "system", "content": TICKETS_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
        )

        usage = response.usage
        if usage:
            trace["input_tokens"] = usage.prompt_tokens
            trace["output_tokens"] = usage.completion_tokens

    raw = json.loads(response.choices[0].message.content)
    epics = [Epic(**e) for e in raw["epics"]]
    total_stories = sum(len(e.stories) for e in epics)

    return TicketsResponse(
        epics=epics,
        total_story_count=total_stories,
        meta=tracker.build_meta(),
    )
