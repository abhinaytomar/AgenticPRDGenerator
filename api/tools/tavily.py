"""Tavily web-search tool.

Gives the FAQ agent access to public, current information that is not in the
local PM/PRD corpus (e.g. "how does Jira's new PRD template work", recent
frameworks, tool comparisons). Configure with TAVILY_API_KEY.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from tavily import TavilyClient  # type: ignore


@dataclass
class TavilyResult:
    title: str
    url: str
    content: str
    score: float


def tavily_available() -> bool:
    return bool(os.environ.get("TAVILY_API_KEY"))


def tavily_search(query: str, max_results: int = 4) -> list[TavilyResult]:
    """Search the public web via Tavily. Returns [] if not configured/failed."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return []
    try:
        client = TavilyClient(api_key=api_key)
        resp = client.search(
            query=query,
            max_results=max_results,
            search_depth="basic",
        )
    except Exception:
        return []

    results: list[TavilyResult] = []
    for r in resp.get("results", []):
        results.append(
            TavilyResult(
                title=r.get("title", ""),
                url=r.get("url", ""),
                content=r.get("content", ""),
                score=float(r.get("score", 0.0)),
            )
        )
    return results
