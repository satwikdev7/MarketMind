from __future__ import annotations

from uuid import uuid4

from app.agents.graph import build_graph
from app.agents.state import build_initial_state


def main() -> None:
    graph = build_graph()
    thread_id = f"marketmind-{uuid4()}"
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = build_initial_state(
        query="Analyze the competitive landscape of cloud data warehouses",
        vertical="technology",
    )
    result = graph.invoke(initial_state, config=config)
    report = result.get("report")
    print(f"Thread ID: {thread_id}")
    print(f"Graph completed: {report is not None}")
    if report is not None:
        print(f"Report ID: {report.report_id}")
        print(f"Sources cited: {len(report.sources_cited)}")
        print(f"LLM calls made: {result.get('llm_calls_made')}")

    interrupted_thread = f"marketmind-interrupt-{uuid4()}"
    interrupted_config = {"configurable": {"thread_id": interrupted_thread}}
    partial = build_graph().invoke(
        build_initial_state(query="AI note taking competitors", vertical="saas"),
        config=interrupted_config,
        interrupt_after=["researcher"],
    )
    print(f"Interrupted thread reached researcher: {bool(partial.get('research_results'))}")
    resumed = build_graph().invoke(None, config=interrupted_config)
    print(f"Resumed graph completed: {resumed.get('report') is not None}")


if __name__ == "__main__":
    main()
