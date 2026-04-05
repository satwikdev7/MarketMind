from __future__ import annotations

from datetime import datetime, timezone
import json
from uuid import uuid4

from app.config import get_settings
from app.llm.groq_client import get_llm, invoke_structured
from app.llm.output_parser import parse_structured_output
from app.llm.prompts import build_analyst_prompt, build_writer_prompt
from app.models.analysis import AnalysisResult
from app.models.report import IntelligenceReport


def main() -> None:
    analyst_prompt = build_analyst_prompt(
        query="Analyze the competitive landscape of cloud data warehouses",
        vertical="technology",
        rag_context=[
            "Source: https://example.com/snowflake - Snowflake focuses on cloud-native data warehousing and enterprise analytics.",
            "Source: https://example.com/databricks - Databricks differentiates with a lakehouse architecture and strong AI positioning.",
            "Source: https://example.com/google-bigquery - BigQuery competes on native Google Cloud integration and serverless pricing.",
        ],
    )
    analyst_result = invoke_structured(analyst_prompt, role="analyst", model_class=AnalysisResult)
    print(f"Analyst competitor profiles: {len(analyst_result.competitor_profiles)}")
    print(f"Analyst SWOT target: {analyst_result.swot_analysis.target}")

    writer_prompt = build_writer_prompt(
        query="Analyze the competitive landscape of cloud data warehouses",
        vertical="technology",
        competitor_profiles_json=json.dumps(
            [item.model_dump() for item in analyst_result.competitor_profiles]
        ),
        competitive_signals_json=json.dumps(
            [item.model_dump() for item in analyst_result.competitive_signals]
        ),
        swot_analysis_json=analyst_result.swot_analysis.model_dump_json(),
        sources_cited=["https://example.com/snowflake", "https://example.com/databricks"],
    )
    writer_result = invoke_structured(writer_prompt, role="writer", model_class=IntelligenceReport)
    print(f"Writer report id: {writer_result.report_id}")
    print(f"Writer sections: {len(writer_result.sections)}")

    malformed = (
        '```json\n{"report_id":"'
        + str(uuid4())
        + '","query":"test","vertical":"technology","generated_at":"'
        + datetime.now(timezone.utc).isoformat()
        + '","executive_summary":"summary","competitor_profiles":[],"swot_analysis":{"target":"Market","strengths":[],"weaknesses":[],"opportunities":[],"threats":[]},"competitive_signals":[],"key_trends":["trend"],"strategic_recommendations":["rec"],"sources_cited":["https://example.com"],"total_sources_searched":1,"generation_time_sec":1.0,"llm_calls_made":1,"sections":[{"title":"Executive Summary","content":"summary","order":1}]'
        "\n```"
    )
    repaired = parse_structured_output(malformed, IntelligenceReport)
    print(f"Malformed JSON repair OK: {repaired.vertical}")

    settings = get_settings()
    print(f"Researcher model: {get_llm('researcher').model_name or settings.llm_secondary_model}")
    print(f"Analyst model: {get_llm('analyst').model_name or settings.llm_secondary_model}")
    print(f"Writer model: {get_llm('writer').model_name or settings.llm_primary_model}")


if __name__ == "__main__":
    main()
