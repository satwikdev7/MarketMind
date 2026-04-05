from __future__ import annotations

import operator
from typing import Annotated, Optional, TypedDict

from app.models.analysis import CompetitorProfile, CompetitiveSignal, SWOTAnalysis
from app.models.query import VerticalConfig
from app.models.report import IntelligenceReport
from app.models.research import ScrapedContent, SearchResult


class AgentState(TypedDict):
    query: str
    vertical: str
    vertical_config: VerticalConfig
    research_results: Annotated[list[SearchResult], operator.add]
    scraped_content: Annotated[list[ScrapedContent], operator.add]
    research_quality_score: float
    rag_context: list[str]
    competitor_profiles: list[CompetitorProfile]
    competitive_signals: list[CompetitiveSignal]
    swot_analysis: Optional[SWOTAnalysis]
    report: Optional[IntelligenceReport]
    sources_cited: list[str]
    errors: Annotated[list[str], operator.add]
    retry_count: int
    route_decision: str
    llm_calls_made: int
