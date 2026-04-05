from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.agents.graph import run_pipeline
from app.database import create_run_history, get_schedule, update_schedule_run_times


def run_scheduled_report(schedule_id: str) -> dict:
    schedule = get_schedule(schedule_id)
    if schedule is None:
        raise ValueError(f"Schedule {schedule_id} not found")

    run_id = str(uuid4())
    started_at = datetime.now(timezone.utc).isoformat()
    create_run_history(
        run_id=run_id,
        schedule_id=schedule_id,
        status="running",
        started_at=started_at,
    )

    try:
        result = run_pipeline(query=schedule.query, vertical=schedule.vertical, schedule_id=schedule_id)
        report = result.get("report")
        completed_at = datetime.now(timezone.utc)
        create_run_history(
            run_id=run_id,
            schedule_id=schedule_id,
            report_id=report.report_id if report else None,
            status="completed",
            started_at=started_at,
            completed_at=completed_at.isoformat(),
        )
        return result
    except Exception as exc:
        completed_at = datetime.now(timezone.utc).isoformat()
        create_run_history(
            run_id=run_id,
            schedule_id=schedule_id,
            status="failed",
            started_at=started_at,
            completed_at=completed_at,
            error_message=str(exc),
        )
        raise


def sync_schedule_next_run(schedule_id: str, next_run: datetime | None) -> None:
    update_schedule_run_times(
        schedule_id,
        last_run=None,
        next_run=next_run,
    )
