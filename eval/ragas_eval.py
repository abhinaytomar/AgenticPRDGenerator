"""Optional RAGAS evaluation (RAG-specific metrics).

RAGAS is version-sensitive; this targets ragas >= 0.2. It is called only when
`python -m eval.run_eval --ragas` is passed, and any failure is caught by the
caller so the core harness still produces a report. Install with:

    pip install -r eval/requirements-eval.txt

Metrics: faithfulness, answer/response relevancy, context precision (with
reference), and context recall. RAGAS uses OpenAI by default, so OPENAI_API_KEY
must be set (it is, via .env.local).
"""

from __future__ import annotations


def run_ragas(samples: list[dict]) -> dict:
    """Score a list of {question, answer, contexts, ground_truth} with RAGAS.

    Returns {metric_name: mean_score}. Raises on import/config errors (caller
    catches).
    """
    from ragas import evaluate  # type: ignore
    from ragas.dataset_schema import EvaluationDataset, SingleTurnSample  # type: ignore
    from ragas.metrics import (  # type: ignore
        Faithfulness,
        ResponseRelevancy,
        LLMContextPrecisionWithReference,
        LLMContextRecall,
    )

    if not samples:
        return {}

    dataset = EvaluationDataset(samples=[
        SingleTurnSample(
            user_input=s["question"],
            response=s["answer"],
            retrieved_contexts=s["contexts"],
            reference=s["ground_truth"],
        )
        for s in samples
    ])

    metrics = [
        Faithfulness(),
        ResponseRelevancy(),
        LLMContextPrecisionWithReference(),
        LLMContextRecall(),
    ]

    result = evaluate(dataset=dataset, metrics=metrics)

    # Normalise to {metric: mean}. `result` supports to_pandas() across 0.2.x.
    scores: dict = {}
    try:
        df = result.to_pandas()
        skip = {"user_input", "response", "retrieved_contexts", "reference"}
        for col in df.columns:
            if col in skip:
                continue
            try:
                scores[col] = round(float(df[col].mean()), 3)
            except (TypeError, ValueError):
                continue
    except Exception:
        # Fall back to dict-like access.
        for k, v in dict(result).items():
            try:
                scores[k] = round(float(v), 3)
            except (TypeError, ValueError):
                continue
    return scores
