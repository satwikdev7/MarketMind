from __future__ import annotations

from app.agents.graph import run_pipeline
from app.database import initialize_database, list_recent_run_history, list_reports, list_schedules
from app.scheduler.scheduler import create_schedule, get_scheduler, pause_schedule, refresh_schedule_metadata, remove_schedule, resume_schedule
from app.verticals.registry import list_vertical_options


def main() -> None:
    import streamlit as st

    initialize_database()
    get_scheduler()

    st.set_page_config(page_title="MarketMind", layout="wide")
    st.title("MarketMind")
    st.caption("Autonomous competitive intelligence powered by LangGraph, Groq, and ChromaDB.")

    _render_sidebar(st)

    tab_new_report, tab_schedules, tab_history = st.tabs(
        ["New Report", "Scheduled Reports", "Run History"]
    )

    with tab_new_report:
        _render_new_report_tab(st)

    with tab_schedules:
        _render_schedule_tab(st)

    with tab_history:
        _render_history_tab(st)


def _render_sidebar(st) -> None:
    reports = list_reports(limit=10)
    schedules = list_schedules()
    st.sidebar.header("System Status")
    st.sidebar.metric("Recent Reports", len(reports))
    st.sidebar.metric("Configured Schedules", len(schedules))
    st.sidebar.caption("Groq, Tavily, ChromaDB, and SQLite are wired through the backend.")


def _render_new_report_tab(st) -> None:
    st.subheader("Generate Report")
    vertical_options = list_vertical_options()
    labels = {vertical_id: display_name for vertical_id, display_name in vertical_options}

    with st.form("new_report_form"):
        query = st.text_input(
            "Query",
            placeholder="Analyze the competitive landscape of cloud data warehouses",
        )
        vertical = st.selectbox(
            "Vertical",
            options=[item[0] for item in vertical_options],
            format_func=lambda value: labels[value],
        )
        submitted = st.form_submit_button("Generate Report")

    if submitted:
        if not query.strip():
            st.error("Enter a query before generating a report.")
            return
        with st.spinner("Running Researcher -> Analyst -> Writer pipeline..."):
            result = run_pipeline(query=query.strip(), vertical=vertical)
        report = result.get("report")
        if report is None:
            st.error("Pipeline completed without a report.")
            return
        st.success("Report generated successfully.")
        _render_report(st, report)


def _render_report(st, report) -> None:
    st.markdown("### Executive Summary")
    st.write(report.executive_summary)

    st.markdown("### Competitor Profiles")
    if report.competitor_profiles:
        for profile in report.competitor_profiles:
            with st.expander(f"{profile.name} | {profile.market_position}"):
                st.write(profile.description)
                st.markdown("**Strengths**")
                st.write("\n".join(f"- {item}" for item in profile.strengths) or "- None")
                st.markdown("**Weaknesses**")
                st.write("\n".join(f"- {item}" for item in profile.weaknesses) or "- None")
                st.markdown("**Recent Moves**")
                st.write("\n".join(f"- {item}" for item in profile.recent_moves) or "- None")
    else:
        st.info("No grounded competitor profiles were returned for this run.")

    st.markdown("### Strategic Recommendations")
    for item in report.strategic_recommendations:
        st.write(f"- {item}")

    st.markdown("### Sources")
    for url in report.sources_cited:
        st.markdown(f"- [{url}]({url})")


def _render_schedule_tab(st) -> None:
    st.subheader("Create Schedule")
    vertical_options = list_vertical_options()
    labels = {vertical_id: display_name for vertical_id, display_name in vertical_options}

    with st.form("schedule_form"):
        query = st.text_input(
            "Scheduled Query",
            placeholder="Track AI note taking competitors",
            key="scheduled_query",
        )
        vertical = st.selectbox(
            "Scheduled Vertical",
            options=[item[0] for item in vertical_options],
            format_func=lambda value: labels[value],
            key="scheduled_vertical",
        )
        interval_hours = st.number_input(
            "Run every N hours",
            min_value=1,
            max_value=168,
            value=24,
            step=1,
        )
        submitted = st.form_submit_button("Create Schedule")

    if submitted:
        if not query.strip():
            st.error("Enter a query before creating a schedule.")
        else:
            schedule = create_schedule(query=query.strip(), vertical=vertical, interval_hours=int(interval_hours))
            st.success(f"Created schedule {schedule.schedule_id}")

    st.markdown("### Active Schedules")
    schedules = [refresh_schedule_metadata(item.schedule_id) or item for item in list_schedules()]
    if not schedules:
        st.info("No schedules configured yet.")
        return

    for schedule in schedules:
        with st.expander(f"{schedule.vertical} | {schedule.query}"):
            st.write(f"Schedule ID: {schedule.schedule_id}")
            st.write(f"Active: {schedule.is_active}")
            st.write(f"Every: {schedule.interval_hours} hours" if schedule.interval_hours else f"Cron: {schedule.cron_expression}")
            st.write(f"Last run: {schedule.last_run or 'Not yet'}")
            st.write(f"Next run: {schedule.next_run or 'Not scheduled'}")
            col1, col2, col3 = st.columns(3)
            if col1.button("Pause", key=f"pause_{schedule.schedule_id}"):
                pause_schedule(schedule.schedule_id)
                st.rerun()
            if col2.button("Resume", key=f"resume_{schedule.schedule_id}"):
                resume_schedule(schedule.schedule_id)
                st.rerun()
            if col3.button("Delete", key=f"delete_{schedule.schedule_id}"):
                remove_schedule(schedule.schedule_id)
                st.rerun()


def _render_history_tab(st) -> None:
    st.subheader("Recent Runs")
    recent_runs = list_recent_run_history(limit=20)
    if recent_runs:
        st.dataframe(recent_runs, use_container_width=True)
    else:
        st.info("No run history yet.")

    st.markdown("### Recent Reports")
    reports = list_reports(limit=10)
    for item in reports:
        report = item["report_json"]
        with st.expander(f"{item['generated_at']} | {item['vertical']} | {item['query']}"):
            st.write(report["executive_summary"])


if __name__ == "__main__":
    main()
