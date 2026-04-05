from __future__ import annotations

from app.rag.retriever import retrieve_relevant_chunks
from app.rag.vector_store import collection_stats, ingest_research_bundle
from app.tools.search_orchestrator import run_search_pipeline
from app.verticals.registry import get_vertical_config


def main() -> None:
    bundle = run_search_pipeline(
        query="cloud data warehouse",
        vertical_config=get_vertical_config("technology"),
        scrape_limit=5,
    )
    ingested_count = ingest_research_bundle(bundle)
    print(f"Ingested chunks: {ingested_count}")
    print(f"Collection stats: {collection_stats('technology')}")

    retrieved = retrieve_relevant_chunks(
        query="Snowflake Databricks competition",
        vertical="technology",
        top_k=5,
        metadata_filter={"vertical": "technology"},
    )
    print(f"Retrieved chunks: {len(retrieved)}")
    if retrieved:
        first = retrieved[0]
        print(f"Top metadata: {first['metadata']}")
        print(f"Top snippet: {first['content'][:250]}")


if __name__ == "__main__":
    main()
