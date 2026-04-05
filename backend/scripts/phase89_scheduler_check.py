from __future__ import annotations

from app.database import list_schedules
from app.scheduler.scheduler import create_schedule, get_scheduler, pause_schedule, remove_schedule, resume_schedule


def main() -> None:
    scheduler = get_scheduler()
    print(f"Scheduler running: {scheduler.running}")

    schedule = create_schedule(
        query="Track AI note taking competitors",
        vertical="saas",
        interval_hours=24,
    )
    print(f"Created schedule: {schedule.schedule_id}")
    print(f"Total schedules: {len(list_schedules())}")

    pause_schedule(schedule.schedule_id)
    print("Paused schedule")
    resume_schedule(schedule.schedule_id)
    print("Resumed schedule")

    remove_schedule(schedule.schedule_id)
    print("Removed schedule")


if __name__ == "__main__":
    main()
