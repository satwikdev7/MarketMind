from __future__ import annotations

import sqlite3
from functools import lru_cache
from uuid import uuid4

from langgraph.checkpoint.sqlite import JsonPlusSerializer, SqliteSaver
from langgraph.graph import END, START, StateGraph

from app.agents.state import build_initial_state
from app.agents.analyst import analyst_node
from app.agents.researcher import researcher_node
from app.agents.router import route_after_router, router_node
from app.agents.writer import writer_node
from app.config import get_settings
from app.models.state import AgentState


@lru_cache(maxsize=1)
def get_checkpointer() -> SqliteSaver:
    settings = get_settings()
    connection = sqlite3.connect(settings.checkpoint_file, check_same_thread=False)
    serde = JsonPlusSerializer(
        allowed_msgpack_modules=[
            ("app.models.query", "VerticalConfig"),
            ("app.models.research", "SearchResult"),
            ("app.models.research", "ScrapedContent"),
            ("app.models.analysis", "CompetitorProfile"),
            ("app.models.analysis", "CompetitiveSignal"),
            ("app.models.analysis", "SWOTEntry"),
            ("app.models.analysis", "SWOTAnalysis"),
            ("app.models.report", "ReportSection"),
            ("app.models.report", "IntelligenceReport"),
        ]
    )
    return SqliteSaver(connection, serde=serde)


@lru_cache(maxsize=1)
def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("researcher", researcher_node)
    builder.add_node("router", router_node)
    builder.add_node("analyst", analyst_node)
    builder.add_node("writer", writer_node)

    builder.add_edge(START, "researcher")
    builder.add_edge("researcher", "router")
    builder.add_conditional_edges(
        "router",
        route_after_router,
        {
            "researcher": "researcher",
            "analyst": "analyst",
        },
    )
    builder.add_edge("analyst", "writer")
    builder.add_edge("writer", END)

    return builder.compile(checkpointer=get_checkpointer())


def run_pipeline(query: str, vertical: str, schedule_id: str | None = None) -> dict:
    thread_id = f"marketmind-{schedule_id or uuid4()}"
    config = {"configurable": {"thread_id": thread_id}}
    result = build_graph().invoke(build_initial_state(query=query, vertical=vertical), config=config)
    report = result.get("report")
    if report is not None and schedule_id:
        report.schedule_id = schedule_id if hasattr(report, "schedule_id") else None
    return result
