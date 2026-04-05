from __future__ import annotations

from app.models.state import AgentState
from app.rag.vector_store import ingest_research_bundle
from app.tools.search_orchestrator import run_search_pipeline
from app.verticals.registry import get_vertical_config


def researcher_node(state: AgentState) -> dict:
    vertical_config = state.get("vertical_config") or get_vertical_config(state["vertical"])
    query = _build_research_query(state)
    bundle = run_search_pipeline(query=query, vertical_config=vertical_config, scrape_limit=5)
    ingested_chunks = ingest_research_bundle(bundle)

    errors: list[str] = []
    if not bundle.search_results:
        errors.append("No search results were collected from live sources.")
    if ingested_chunks == 0:
        errors.append("No chunks were ingested into the vector store.")

    return {
        "vertical_config": vertical_config,
        "research_results": bundle.search_results,
        "scraped_content": bundle.scraped_content,
        "research_quality_score": bundle.quality_score,
        "sources_cited": [result.url for result in bundle.search_results[:15]],
        "errors": errors,
        "route_decision": "research_complete",
    }


def _build_research_query(state: AgentState) -> str:
    query = state["query"]
    retry_count = state.get("retry_count", 0)
    if retry_count == 1:
        return f"{query} competitors market trends funding product launch"
    if retry_count >= 2:
        return f"{query} alternatives industry leaders partnerships news"
    return query
