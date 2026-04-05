from __future__ import annotations

from app.models.analysis import AnalysisResult, CompetitorProfile, CompetitiveSignal, SWOTAnalysis
from app.llm.groq_client import invoke_structured
from app.llm.prompts import build_analyst_prompt
from app.models.state import AgentState
from app.rag.retriever import retrieve_relevant_chunks


def analyst_node(state: AgentState) -> dict:
    retrieved = retrieve_relevant_chunks(
        query=state["query"],
        vertical=state["vertical"],
        top_k=10,
        metadata_filter={"vertical": state["vertical"]},
    )
    rag_context = [_format_chunk(item) for item in retrieved]
    analysis = invoke_structured(
        build_analyst_prompt(
            query=state["query"],
            vertical=state["vertical"],
            rag_context=rag_context,
        ),
        role="analyst",
        model_class=AnalysisResult,
    )
    allowed_urls = {_extract_url(result) for result in state.get("research_results", [])}
    allowed_urls.discard("")
    grounded = validate_grounding(analysis, allowed_urls=allowed_urls, retrieved_chunks=retrieved)

    return {
        "rag_context": rag_context,
        "competitor_profiles": grounded.competitor_profiles,
        "competitive_signals": grounded.competitive_signals,
        "swot_analysis": grounded.swot_analysis,
        "llm_calls_made": state.get("llm_calls_made", 0) + 1,
    }


def validate_grounding(
    analysis: AnalysisResult,
    allowed_urls: set[str],
    retrieved_chunks: list[dict],
) -> AnalysisResult:
    filtered_profiles: list[CompetitorProfile] = []
    for profile in analysis.competitor_profiles:
        inferred_urls = infer_profile_urls(profile.name, retrieved_chunks)
        candidate_urls = [url for url in profile.source_urls if url in allowed_urls]
        if not candidate_urls:
            candidate_urls = [url for url in inferred_urls if url in allowed_urls]
        if not candidate_urls:
            continue
        filtered_profiles.append(
            CompetitorProfile(
                name=profile.name,
                description=profile.description,
                market_position=profile.market_position,
                strengths=profile.strengths,
                weaknesses=profile.weaknesses,
                recent_moves=profile.recent_moves,
                source_urls=candidate_urls[:3],
            )
        )

    filtered_signals: list[CompetitiveSignal] = []
    for signal in analysis.competitive_signals:
        if signal.source_url in allowed_urls:
            filtered_signals.append(signal)
            continue
        inferred_urls = infer_profile_urls(signal.company, retrieved_chunks)
        if inferred_urls:
            filtered_signals.append(
                CompetitiveSignal(
                    signal_type=signal.signal_type,
                    company=signal.company,
                    description=signal.description,
                    date=signal.date,
                    impact=signal.impact,
                    source_url=inferred_urls[0],
                )
            )

    swot = analysis.swot_analysis
    swot = SWOTAnalysis(
        target=swot.target,
        strengths=[entry for entry in swot.strengths if entry.supporting_evidence],
        weaknesses=[entry for entry in swot.weaknesses if entry.supporting_evidence],
        opportunities=[entry for entry in swot.opportunities if entry.supporting_evidence],
        threats=[entry for entry in swot.threats if entry.supporting_evidence],
    )

    return AnalysisResult(
        competitor_profiles=filtered_profiles,
        competitive_signals=filtered_signals,
        swot_analysis=swot,
    )


def infer_profile_urls(company_name: str, retrieved_chunks: list[dict]) -> list[str]:
    company_terms = [term.lower() for term in company_name.split() if term.strip()]
    if not company_terms:
        return []

    matches: list[str] = []
    for chunk in retrieved_chunks:
        metadata = chunk.get("metadata", {}) or {}
        content = chunk.get("content", "").lower()
        title = str(metadata.get("title", "")).lower()
        url = str(metadata.get("url", ""))
        if not url:
            continue
        if any(term in content or term in title for term in company_terms):
            matches.append(url)

    seen: set[str] = set()
    ordered_matches: list[str] = []
    for url in matches:
        if url in seen:
            continue
        seen.add(url)
        ordered_matches.append(url)
    return ordered_matches


def _format_chunk(item: dict) -> str:
    metadata = item.get("metadata", {})
    title = metadata.get("title", "Untitled")
    url = metadata.get("url", "")
    return f"Source: {url} | Title: {title}\n{item.get('content', '')}"


def _extract_url(result: object) -> str:
    if isinstance(result, dict):
        return str(result.get("url", ""))
    return str(getattr(result, "url", ""))
