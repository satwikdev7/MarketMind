from __future__ import annotations

from app.models.state import AgentState


QUALITY_THRESHOLD = 0.6
MIN_SCRAPED_DOCUMENTS = 3
MAX_RETRIES = 2


def router_node(state: AgentState) -> dict:
    quality_score = state.get("research_quality_score", 0.0)
    scraped_count = len(
        [item for item in state.get("scraped_content", []) if _scrape_success(item)]
    )
    retry_count = state.get("retry_count", 0)

    if quality_score >= QUALITY_THRESHOLD and scraped_count >= MIN_SCRAPED_DOCUMENTS:
        return {"route_decision": "analyst"}
    if retry_count < MAX_RETRIES:
        return {
            "retry_count": retry_count + 1,
            "route_decision": "researcher",
            "errors": [f"Research quality too low: score={quality_score}, scraped={scraped_count}"],
        }
    return {
        "route_decision": "analyst",
        "errors": ["Proceeding with limited research after retries were exhausted."],
    }


def route_after_router(state: AgentState) -> str:
    return state.get("route_decision", "analyst")


def _scrape_success(item: object) -> bool:
    if isinstance(item, dict):
        return bool(item.get("scrape_success"))
    return bool(getattr(item, "scrape_success", False))
