from __future__ import annotations

from datetime import datetime, timezone

import feedparser

from app.config import get_settings
from app.models.query import VerticalConfig
from app.models.research import SearchResult
from app.utils.text_utils import normalize_whitespace


def fetch_vertical_rss(vertical_config: VerticalConfig) -> list[SearchResult]:
    settings = get_settings()
    fetched_at = datetime.now(timezone.utc).isoformat()
    results: list[SearchResult] = []

    for feed_url in vertical_config.rss_feeds:
        try:
            parsed = feedparser.parse(feed_url)
        except Exception:
            continue
        for item in parsed.entries[: settings.rss_max_entries_per_feed]:
            title = normalize_whitespace(getattr(item, "title", ""))
            summary = normalize_whitespace(getattr(item, "summary", ""))
            link = getattr(item, "link", "")
            published_date = getattr(item, "published", None)
            if not link:
                continue
            results.append(
                SearchResult(
                    url=link,
                    title=title,
                    snippet=summary,
                    source="rss",
                    published_date=published_date,
                    relevance_score=0.7,
                    fetched_at=fetched_at,
                )
            )

    return results
