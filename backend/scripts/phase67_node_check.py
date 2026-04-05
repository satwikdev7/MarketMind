from __future__ import annotations

from app.agents.analyst import analyst_node
from app.agents.researcher import researcher_node
from app.agents.router import route_after_router, router_node
from app.agents.state import build_initial_state
from app.agents.writer import writer_node
from app.database import get_report


def main() -> None:
    state = build_initial_state(query="cloud data warehouse", vertical="technology")

    research_update = researcher_node(state)
    research_state = {**state, **research_update}
    print(
        f"Researcher: results={len(research_update['research_results'])}, "
        f"scrapes={len(research_update['scraped_content'])}, "
        f"quality={research_update['research_quality_score']}"
    )

    router_update = router_node(research_state)
    routed_state = {**research_state, **router_update}
    print(
        f"Router: decision={route_after_router(routed_state)}, "
        f"retry_count={routed_state['retry_count']}"
    )
    low_quality_route = router_node(
        {
            **state,
            "research_quality_score": 0.1,
            "scraped_content": [],
            "retry_count": 0,
        }
    )
    print(f"Router low-quality branch: {low_quality_route['route_decision']}")

    analyst_update = analyst_node(routed_state)
    analyst_state = {**routed_state, **analyst_update}
    print(
        f"Analyst: profiles={len(analyst_update['competitor_profiles'])}, "
        f"signals={len(analyst_update['competitive_signals'])}"
    )

    writer_update = writer_node(analyst_state)
    report = writer_update["report"]
    saved = get_report(report.report_id)
    print(f"Writer: report_id={report.report_id}, sections={len(report.sections)}")
    print(f"Writer persisted: {saved is not None}")


if __name__ == "__main__":
    main()
