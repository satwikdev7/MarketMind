from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.database import get_connection, initialize_database
from app.models.analysis import SWOTAnalysis, SWOTEntry
from app.models.query import QueryInput
from app.models.report import IntelligenceReport, ReportSection


def main() -> None:
    query = QueryInput(query="Analyze cloud data warehouse competition", vertical="technology")
    swot = SWOTAnalysis(
        target="Cloud Data Warehouse Market",
        strengths=[SWOTEntry(point="High growth", supporting_evidence="Demand remains strong")],
        weaknesses=[SWOTEntry(point="High switching cost", supporting_evidence="Migration is complex")],
        opportunities=[SWOTEntry(point="AI features", supporting_evidence="Vendors are adding copilots")],
        threats=[SWOTEntry(point="Price pressure", supporting_evidence="Warehouse vendors compete heavily")],
    )
    report = IntelligenceReport(
        report_id=str(uuid4()),
        query=query.query,
        vertical=query.vertical,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executive_summary="Sample summary",
        competitor_profiles=[],
        swot_analysis=swot,
        competitive_signals=[],
        key_trends=["Usage-based pricing"],
        strategic_recommendations=["Track differentiation beyond price"],
        sources_cited=["https://example.com"],
        total_sources_searched=1,
        generation_time_sec=1.2,
        llm_calls_made=0,
        sections=[ReportSection(title="Executive Summary", content="Sample summary", order=1)],
    )

    initialize_database()
    with get_connection() as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }

    print(query.model_dump_json(indent=2))
    print(report.model_dump_json(indent=2))
    print(f"Database tables: {sorted(tables)}")


if __name__ == "__main__":
    main()
