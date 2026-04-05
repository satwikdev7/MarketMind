from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
from uuid import uuid4

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.database import (
    delete_schedule,
    get_schedule,
    list_schedules,
    save_schedule,
    update_schedule_run_times,
    update_schedule_status,
)
from app.models.report import ScheduledReport
from app.scheduler.jobs import run_scheduled_report


def _job_id(schedule_id: str) -> str:
    return f"schedule:{schedule_id}"


@lru_cache(maxsize=1)
def get_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="America/New_York")
    scheduler.start(paused=False)
    load_schedules_into_scheduler(scheduler)
    return scheduler


def load_schedules_into_scheduler(scheduler: BackgroundScheduler) -> None:
    for schedule in list_schedules():
        if schedule.is_active:
            _schedule_job(scheduler, schedule)


def create_schedule(
    *,
    query: str,
    vertical: str,
    interval_hours: int | None = None,
    cron_expression: str | None = None,
) -> ScheduledReport:
    if not interval_hours and not cron_expression:
        raise ValueError("Either interval_hours or cron_expression must be provided")

    schedule = ScheduledReport(
        schedule_id=str(uuid4()),
        query=query,
        vertical=vertical,
        cron_expression=cron_expression,
        interval_hours=interval_hours,
        is_active=True,
        last_run=None,
        next_run=None,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    save_schedule(schedule)
    job = _schedule_job(get_scheduler(), schedule)
    update_schedule_run_times(schedule.schedule_id, last_run=None, next_run=job.next_run_time)
    return get_schedule(schedule.schedule_id) or schedule


def pause_schedule(schedule_id: str) -> None:
    scheduler = get_scheduler()
    scheduler.pause_job(_job_id(schedule_id))
    update_schedule_status(schedule_id, is_active=False)


def resume_schedule(schedule_id: str) -> None:
    scheduler = get_scheduler()
    scheduler.resume_job(_job_id(schedule_id))
    job = scheduler.get_job(_job_id(schedule_id))
    update_schedule_status(
        schedule_id,
        is_active=True,
        next_run=job.next_run_time.isoformat() if job and job.next_run_time else None,
    )


def remove_schedule(schedule_id: str) -> None:
    scheduler = get_scheduler()
    if scheduler.get_job(_job_id(schedule_id)):
        scheduler.remove_job(_job_id(schedule_id))
    delete_schedule(schedule_id)


def refresh_schedule_metadata(schedule_id: str) -> ScheduledReport | None:
    scheduler = get_scheduler()
    job = scheduler.get_job(_job_id(schedule_id))
    schedule = get_schedule(schedule_id)
    if schedule is None:
        return None
    update_schedule_status(
        schedule_id,
        is_active=schedule.is_active,
        next_run=job.next_run_time.isoformat() if job and job.next_run_time else None,
    )
    return get_schedule(schedule_id)


def _schedule_job(scheduler: BackgroundScheduler, schedule: ScheduledReport):
    trigger = _build_trigger(schedule)
    job = scheduler.add_job(
        func=_scheduled_job_wrapper,
        trigger=trigger,
        id=_job_id(schedule.schedule_id),
        replace_existing=True,
        kwargs={"schedule_id": schedule.schedule_id},
    )
    return job


def _scheduled_job_wrapper(schedule_id: str) -> None:
    result = run_scheduled_report(schedule_id)
    report = result.get("report")
    scheduler = get_scheduler()
    job = scheduler.get_job(_job_id(schedule_id))
    update_schedule_run_times(
        schedule_id,
        last_run=datetime.now(timezone.utc),
        next_run=job.next_run_time if job else None,
    )
    if report is None:
        raise RuntimeError(f"Scheduled run for {schedule_id} completed without a report")


def _build_trigger(schedule: ScheduledReport):
    if schedule.interval_hours:
        return IntervalTrigger(hours=schedule.interval_hours, timezone="America/New_York")
    if schedule.cron_expression:
        minute, hour, day, month, day_of_week = schedule.cron_expression.split()
        return CronTrigger(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
            timezone="America/New_York",
        )
    raise ValueError("Schedule must define either interval_hours or cron_expression")
