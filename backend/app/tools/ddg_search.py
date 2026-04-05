from __future__ import annotations

from datetime import datetime, timezone

from ddgs import DDGS

from app.config import get_settings
from app.models.research import SearchResult
from app.utils.text_utils import normalize_whitespace


def search_duckduckgo(query: str, max_results: int | None = None) -> list[SearchResult]:
    settings = get_settings()
    fetched_at = datetime.now(timezone.utc).isoformat()
    results: list[SearchResult] = []

    try:
        with DDGS() as ddgs:
            for index, item in enumerate(
                ddgs.text(query, max_results=max_results or settings.ddg_max_results),
                start=1,
            ):
                results.append(
                    SearchResult(
                        url=item.get("href", ""),
                        title=normalize_whitespace(item.get("title", "")),
                        snippet=normalize_whitespace(item.get("body", "")),
                        source="duckduckgo",
                        relevance_score=max(0.0, 1.0 - ((index - 1) * 0.05)),
                        fetched_at=fetched_at,
                    )
                )
    except Exception:
        return []

    return [result for result in results if result.url]
