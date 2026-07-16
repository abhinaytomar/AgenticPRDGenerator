"""Observability utilities: request IDs, step tracing, latency/token/cost tracking."""

from __future__ import annotations

import logging
import time
import uuid
from contextlib import contextmanager
from typing import Generator

from api.models import StepMeta, StepTrace

logger = logging.getLogger("prd_generator")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Cost per 1K tokens (approximate for gpt-5-nano)
INPUT_COST_PER_1K = 0.00010
OUTPUT_COST_PER_1K = 0.00040


def new_request_id() -> str:
    return str(uuid.uuid4())[:12]


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    return (input_tokens / 1000) * INPUT_COST_PER_1K + (output_tokens / 1000) * OUTPUT_COST_PER_1K


class StepTracker:
    """Accumulates step traces for a single request."""

    def __init__(self, request_id: str):
        self.request_id = request_id
        self.traces: list[StepTrace] = []
        self._start_time = time.time()

    @contextmanager
    def track_step(self, step_name: str) -> Generator[dict, None, None]:
        """Context manager that tracks latency, tokens, and cost for a step.

        Yields a mutable dict where the caller should set 'input_tokens' and
        'output_tokens' after the LLM call completes.
        """
        result: dict = {"input_tokens": 0, "output_tokens": 0, "success": True}
        start = time.time()
        try:
            yield result
        except Exception:
            result["success"] = False
            raise
        finally:
            elapsed_ms = round((time.time() - start) * 1000, 1)
            total_tokens = result["input_tokens"] + result["output_tokens"]
            cost = estimate_cost(result["input_tokens"], result["output_tokens"])

            trace = StepTrace(
                step=step_name,
                latency_ms=elapsed_ms,
                tokens=total_tokens,
                estimated_cost_usd=round(cost, 6),
                success=result["success"],
            )
            self.traces.append(trace)

            logger.info(
                "request_id=%s step=%s latency_ms=%.1f tokens=%d cost=$%.6f success=%s",
                self.request_id,
                step_name,
                elapsed_ms,
                total_tokens,
                cost,
                result["success"],
            )

    def build_meta(self) -> StepMeta:
        return StepMeta(
            request_id=self.request_id,
            steps=self.traces,
            total_latency_ms=round((time.time() - self._start_time) * 1000, 1),
            total_tokens=sum(t.tokens for t in self.traces),
            estimated_cost_usd=round(sum(t.estimated_cost_usd for t in self.traces), 6),
        )
