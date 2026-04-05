from __future__ import annotations

from app.tools.search_orchestrator import run_search_pipeline, source_breakdown
from app.verticals.registry import get_vertical_config


def main() -> None:
    test_cases = [
        ("cloud data warehouse", "technology"),
        ("digital payments platforms", "finance"),
        ("electric vehicle charging", "automotive"),
    ]

    for query, vertical in test_cases:
        print(f"\n=== Query: {query} | Vertical: {vertical} ===")
        bundle = run_search_pipeline(query, get_vertical_config(vertical), scrape_limit=5)
        print(f"Total sources: {bundle.total_sources}")
        print(f"Unique domains: {bundle.unique_domains}")
        print(f"Quality score: {bundle.quality_score}")
        print(f"Source breakdown: {source_breakdown(bundle.search_results)}")
        successful_scrapes = [item for item in bundle.scraped_content if item.scrape_success]
        print(f"Successful scrapes: {len(successful_scrapes)}")
        if bundle.search_results:
            print(f"Top result: {bundle.search_results[0].title} | {bundle.search_results[0].url}")


if __name__ == "__main__":
    main()
