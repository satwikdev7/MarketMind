from __future__ import annotations

from datetime import datetime, timezone

from tavily import TavilyClient

from app.config import get_settings
from app.models.research import SearchResult
from app.utils.text_utils import normalize_whitespace


def search_tavily(query: str, max_results: int | None = None) -> list[SearchResult]:
    settings = get_settings()
    if not settings.tavily_api_key:
        return []

    client = TavilyClient(api_key=settings.tavily_api_key)
    try:
        response = client.search(
            query=query,
            max_results=max_results or settings.tavily_max_results,
            search_depth=settings.tavily_search_depth,
        )
    except Exception:
        return []

    fetched_at = datetime.now(timezone.utc).isoformat()
    results: list[SearchResult] = []
    for item in response.get("results", []):
        results.append(
            SearchResult(
                url=item.get("url", ""),
                title=normalize_whitespace(item.get("title", "")),
                snippet=normalize_whitespace(item.get("content", "")),
                source="tavily",
                published_date=item.get("published_date"),
                relevance_score=_normalize_score(item.get("score")),
                fetched_at=fetched_at,
            )
        )
    return [result for result in results if result.url]


def _normalize_score(raw_score: float | None) -> float | None:
    if raw_score is None:
        return None
    if raw_score <= 1:
        return max(0.0, min(raw_score, 1.0))
    return max(0.0, min(raw_score / 10.0, 1.0))
