from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from app.database import save_report
from app.llm.groq_client import invoke_structured
from app.llm.prompts import build_writer_prompt
from app.models.report import IntelligenceReport, ReportSection
from app.models.state import AgentState


def writer_node(state: AgentState) -> dict:
    swot_analysis = state.get("swot_analysis")
    if swot_analysis is None:
        raise ValueError("Writer node requires SWOT analysis in state")

    report = invoke_structured(
        build_writer_prompt(
            query=state["query"],
            vertical=state["vertical"],
            competitor_profiles_json=json.dumps(
                [item.model_dump() for item in state.get("competitor_profiles", [])]
            ),
            competitive_signals_json=json.dumps(
                [item.model_dump() for item in state.get("competitive_signals", [])]
            ),
            swot_analysis_json=swot_analysis.model_dump_json(),
            sources_cited=state.get("sources_cited", []),
        ),
        role="writer",
        model_class=IntelligenceReport,
    )
    normalized = normalize_report(report, state)
    save_report(normalized.model_dump())

    return {
        "report": normalized,
        "llm_calls_made": state.get("llm_calls_made", 0) + 1,
    }


def normalize_report(report: IntelligenceReport, state: AgentState) -> IntelligenceReport:
    sections = report.sections or build_fallback_sections(report)
    return IntelligenceReport(
        report_id=report.report_id or str(uuid4()),
        query=state["query"],
        vertical=state["vertical"],
        generated_at=datetime.now(timezone.utc).isoformat(),
        executive_summary=report.executive_summary,
        competitor_profiles=report.competitor_profiles,
        swot_analysis=report.swot_analysis,
        competitive_signals=report.competitive_signals,
        key_trends=report.key_trends,
        strategic_recommendations=report.strategic_recommendations,
        sources_cited=report.sources_cited or state.get("sources_cited", []),
        total_sources_searched=len(state.get("research_results", [])),
        generation_time_sec=max(report.generation_time_sec, 0.0),
        llm_calls_made=state.get("llm_calls_made", 0) + 1,
        sections=sections,
    )


def build_fallback_sections(report: IntelligenceReport) -> list[ReportSection]:
    return [
        ReportSection(title="Executive Summary", content=report.executive_summary, order=1),
        ReportSection(
            title="Key Trends",
            content="\n".join(f"- {item}" for item in report.key_trends),
            order=2,
        ),
        ReportSection(
            title="Strategic Recommendations",
            content="\n".join(f"- {item}" for item in report.strategic_recommendations),
            order=3,
        ),
    ]
