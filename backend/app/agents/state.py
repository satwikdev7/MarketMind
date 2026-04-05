from __future__ import annotations

from app.models.state import AgentState
from app.verticals.registry import get_vertical_config


def build_initial_state(query: str, vertical: str) -> AgentState:
    return AgentState(
        query=query,
        vertical=vertical,
        vertical_config=get_vertical_config(vertical),
        research_results=[],
        scraped_content=[],
        research_quality_score=0.0,
        rag_context=[],
        competitor_profiles=[],
        competitive_signals=[],
        swot_analysis=None,
        report=None,
        sources_cited=[],
        errors=[],
        retry_count=0,
        route_decision="research",
        llm_calls_made=0,
    )
