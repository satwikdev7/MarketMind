from __future__ import annotations

import asyncio
from collections import Counter
from typing import Iterable

from app.models.query import VerticalConfig
from app.models.research import ResearchBundle, ScrapedContent, SearchResult
from app.tools.ddg_search import search_duckduckgo
from app.tools.rss_fetcher import fetch_vertical_rss
from app.tools.tavily_search import search_tavily
from app.tools.web_scraper import scrape_search_results
from app.utils.text_utils import extract_domain


def build_search_queries(query: str, vertical_config: VerticalConfig) -> list[str]:
    values = {"query": query, "vertical": vertical_config.display_name}
    queries = [template.format(**values) for template in vertical_config.search_templates]
    queries.extend(template.format(**values) for template in vertical_config.competitor_discovery_queries)
    deduped: list[str] = []
    seen: set[str] = set()
    for item in queries:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


def run_search_pipeline(query: str, vertical_config: VerticalConfig, scrape_limit: int = 5) -> ResearchBundle:
    search_queries = build_search_queries(query, vertical_config)
    all_results: list[SearchResult] = []

    for search_query in search_queries[:3]:
        all_results.extend(search_tavily(search_query))
        all_results.extend(search_duckduckgo(search_query))

    all_results.extend(fetch_vertical_rss(vertical_config))
    deduplicated = deduplicate_results(all_results)
    ranked_results = rank_results(deduplicated, query=query)
    scraped_content = asyncio.run(scrape_search_results(ranked_results, limit=scrape_limit))
    quality_score = calculate_quality_score(ranked_results, scraped_content)

    return ResearchBundle(
        query=query,
        vertical=vertical_config.vertical_id,
        search_results=ranked_results,
        scraped_content=scraped_content,
        total_sources=len(ranked_results),
        unique_domains=count_unique_domains(ranked_results),
        quality_score=quality_score,
    )


def deduplicate_results(results: Iterable[SearchResult]) -> list[SearchResult]:
    by_url: dict[str, SearchResult] = {}
    for result in results:
        existing = by_url.get(result.url)
        if existing is None:
            by_url[result.url] = result
            continue
        current_score = result.relevance_score or 0.0
        existing_score = existing.relevance_score or 0.0
        if current_score > existing_score:
            by_url[result.url] = result
    return list(by_url.values())


def rank_results(results: Iterable[SearchResult], query: str) -> list[SearchResult]:
    query_terms = {term.lower() for term in query.split() if term.strip()}

    def sort_key(result: SearchResult) -> tuple[float, float]:
        text = f"{result.title} {result.snippet}".lower()
        overlap = sum(1 for term in query_terms if term in text)
        score = result.relevance_score or 0.0
        return (overlap, score)

    return sorted(results, key=sort_key, reverse=True)


def count_unique_domains(results: Iterable[SearchResult]) -> int:
    return len({extract_domain(result.url) for result in results if result.url})


def calculate_quality_score(results: list[SearchResult], scraped_content: list[ScrapedContent]) -> float:
    source_count_component = min(len(results) / 15.0, 1.0)
    domain_count_component = min(count_unique_domains(results) / 5.0, 1.0)
    successful_scrapes = [item for item in scraped_content if item.scrape_success and item.content_length > 0]
    scrape_success_component = (
        len(successful_scrapes) / len(scraped_content) if scraped_content else 0.0
    )
    recent_component = _recent_content_component(results)

    score = (
        (0.3 * source_count_component)
        + (0.3 * domain_count_component)
        + (0.2 * scrape_success_component)
        + (0.2 * recent_component)
    )
    return round(min(score, 1.0), 3)


def source_breakdown(results: Iterable[SearchResult]) -> dict[str, int]:
    return dict(Counter(result.source for result in results))


def _recent_content_component(results: list[SearchResult]) -> float:
    recent_hits = 0
    for result in results:
        if result.published_date:
            recent_hits += 1
    return min(recent_hits / 3.0, 1.0)
