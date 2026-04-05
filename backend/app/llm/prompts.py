from __future__ import annotations

import json

from pydantic import BaseModel

from app.models.analysis import AnalysisResult
from app.models.report import IntelligenceReport


def schema_to_json(model_class: type[BaseModel]) -> str:
    return json.dumps(model_class.model_json_schema(), indent=2)


def build_analyst_prompt(query: str, vertical: str, rag_context: list[str]) -> str:
    context_block = "\n\n".join(rag_context[:10])
    return (
        "You are a competitive intelligence analyst.\n"
        "Extract structured competitive signals from the provided research data.\n"
        "Every claim must be grounded in the provided sources.\n"
        "If you cannot find evidence for a claim, do not include it.\n"
        "Use the exact source URLs that appear in the research data.\n"
        "Prefer 2 to 5 competitor profiles when evidence exists.\n"
        "For each competitor profile, include at least one supporting source URL.\n"
        "Return all SWOT sections even if some are empty arrays.\n"
        "Respond in valid JSON only.\n\n"
        f"Query: {query}\n"
        f"Vertical: {vertical}\n\n"
        "Research Data:\n"
        f"{context_block}\n\n"
        "Instructions:\n"
        "1. competitor_profiles: include only companies explicitly mentioned in the research data.\n"
        "2. competitive_signals: include product launches, funding, partnerships, pricing moves, or market expansion.\n"
        "3. swot_analysis: always include strengths, weaknesses, opportunities, and threats arrays.\n"
        "4. Never use null for required string fields.\n\n"
        "Return JSON matching this schema:\n"
        f"{schema_to_json(AnalysisResult)}"
    )


def build_writer_prompt(
    query: str,
    vertical: str,
    competitor_profiles_json: str,
    competitive_signals_json: str,
    swot_analysis_json: str,
    sources_cited: list[str],
) -> str:
    return (
        "You are a senior competitive intelligence report writer.\n"
        "Use only the analysis data provided. Do not invent facts.\n"
        "Respond in valid JSON only.\n\n"
        f"Query: {query}\n"
        f"Vertical: {vertical}\n\n"
        f"Competitor Profiles: {competitor_profiles_json}\n\n"
        f"Competitive Signals: {competitive_signals_json}\n\n"
        f"SWOT Analysis: {swot_analysis_json}\n\n"
        f"Sources Cited: {json.dumps(sources_cited)}\n\n"
        "Return JSON matching this schema:\n"
        f"{schema_to_json(IntelligenceReport)}"
    )
