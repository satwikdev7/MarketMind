from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Generator

from app.config import get_settings
from app.models.report import ScheduledReport


SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS reports (
        report_id TEXT PRIMARY KEY,
        query TEXT NOT NULL,
        vertical TEXT NOT NULL,
        generated_at TEXT NOT NULL,
        report_json TEXT NOT NULL,
        generation_time_sec REAL,
        llm_calls_made INTEGER,
        total_sources INTEGER,
        schedule_id TEXT,
        FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS schedules (
        schedule_id TEXT PRIMARY KEY,
        query TEXT NOT NULL,
        vertical TEXT NOT NULL,
        cron_expression TEXT,
        interval_hours INTEGER,
        is_active INTEGER DEFAULT 1,
        last_run TEXT,
        next_run TEXT,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS run_history (
        run_id TEXT PRIMARY KEY,
        report_id TEXT,
        schedule_id TEXT,
        started_at TEXT NOT NULL,
        completed_at TEXT,
        status TEXT NOT NULL,
        error_message TEXT,
        tavily_searches_used INTEGER,
        groq_tokens_used INTEGER,
        FOREIGN KEY (report_id) REFERENCES reports(report_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS rate_limits (
        service TEXT NOT NULL,
        period TEXT NOT NULL,
        usage_count INTEGER DEFAULT 0,
        period_start TEXT NOT NULL,
        PRIMARY KEY (service, period)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_reports_vertical ON reports(vertical)",
    "CREATE INDEX IF NOT EXISTS idx_reports_generated_at ON reports(generated_at)",
    "CREATE INDEX IF NOT EXISTS idx_schedules_active ON schedules(is_active)",
    "CREATE INDEX IF NOT EXISTS idx_run_history_status ON run_history(status)",
)


def get_connection() -> sqlite3.Connection:
    settings = get_settings()
    connection = sqlite3.connect(settings.database_file)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def transaction() -> Generator[sqlite3.Connection, None, None]:
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database() -> None:
    with transaction() as connection:
        for statement in SCHEMA_STATEMENTS:
            connection.execute(statement)


def save_report(report: dict[str, Any], schedule_id: str | None = None) -> None:
    initialize_database()
    with transaction() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO reports (
                report_id, query, vertical, generated_at, report_json,
                generation_time_sec, llm_calls_made, total_sources, schedule_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report["report_id"],
                report["query"],
                report["vertical"],
                report["generated_at"],
                json.dumps(report),
                report.get("generation_time_sec"),
                report.get("llm_calls_made"),
                report.get("total_sources_searched"),
                schedule_id,
            ),
        )


def list_reports(limit: int = 50) -> list[dict[str, Any]]:
    initialize_database()
    with transaction() as connection:
        rows = connection.execute(
            """
            SELECT report_id, query, vertical, generated_at, report_json
            FROM reports
            ORDER BY generated_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        {
            "report_id": row["report_id"],
            "query": row["query"],
            "vertical": row["vertical"],
            "generated_at": row["generated_at"],
            "report_json": json.loads(row["report_json"]),
        }
        for row in rows
    ]


def get_report(report_id: str) -> dict[str, Any] | None:
    initialize_database()
    with transaction() as connection:
        row = connection.execute(
            """
            SELECT report_id, query, vertical, generated_at, report_json
            FROM reports
            WHERE report_id = ?
            """,
            (report_id,),
        ).fetchone()

    if row is None:
        return None

    return {
        "report_id": row["report_id"],
        "query": row["query"],
        "vertical": row["vertical"],
        "generated_at": row["generated_at"],
        "report_json": json.loads(row["report_json"]),
    }


def save_schedule(schedule: ScheduledReport) -> None:
    initialize_database()
    with transaction() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO schedules (
                schedule_id, query, vertical, cron_expression, interval_hours,
                is_active, last_run, next_run, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                schedule.schedule_id,
                schedule.query,
                schedule.vertical,
                schedule.cron_expression,
                schedule.interval_hours,
                int(schedule.is_active),
                schedule.last_run,
                schedule.next_run,
                schedule.created_at,
            ),
        )


def list_schedules() -> list[ScheduledReport]:
    initialize_database()
    with transaction() as connection:
        rows = connection.execute(
            """
            SELECT schedule_id, query, vertical, cron_expression, interval_hours,
                   is_active, last_run, next_run, created_at
            FROM schedules
            ORDER BY created_at DESC
            """
        ).fetchall()

    return [
        ScheduledReport(
            schedule_id=row["schedule_id"],
            query=row["query"],
            vertical=row["vertical"],
            cron_expression=row["cron_expression"],
            interval_hours=row["interval_hours"],
            is_active=bool(row["is_active"]),
            last_run=row["last_run"],
            next_run=row["next_run"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


def get_schedule(schedule_id: str) -> ScheduledReport | None:
    initialize_database()
    with transaction() as connection:
        row = connection.execute(
            """
            SELECT schedule_id, query, vertical, cron_expression, interval_hours,
                   is_active, last_run, next_run, created_at
            FROM schedules
            WHERE schedule_id = ?
            """,
            (schedule_id,),
        ).fetchone()

    if row is None:
        return None

    return ScheduledReport(
        schedule_id=row["schedule_id"],
        query=row["query"],
        vertical=row["vertical"],
        cron_expression=row["cron_expression"],
        interval_hours=row["interval_hours"],
        is_active=bool(row["is_active"]),
        last_run=row["last_run"],
        next_run=row["next_run"],
        created_at=row["created_at"],
    )


def delete_schedule(schedule_id: str) -> None:
    initialize_database()
    with transaction() as connection:
        connection.execute("DELETE FROM schedules WHERE schedule_id = ?", (schedule_id,))


def update_schedule_status(
    schedule_id: str,
    *,
    is_active: bool,
    last_run: str | None = None,
    next_run: str | None = None,
) -> None:
    initialize_database()
    with transaction() as connection:
        connection.execute(
            """
            UPDATE schedules
            SET is_active = ?, last_run = COALESCE(?, last_run), next_run = COALESCE(?, next_run)
            WHERE schedule_id = ?
            """,
            (int(is_active), last_run, next_run, schedule_id),
        )


def update_schedule_run_times(
    schedule_id: str,
    *,
    last_run: datetime | None,
    next_run: datetime | None,
) -> None:
    update_schedule_status(
        schedule_id,
        is_active=True,
        last_run=last_run.isoformat() if last_run else None,
        next_run=next_run.isoformat() if next_run else None,
    )


def create_run_history(
    *,
    run_id: str,
    schedule_id: str | None,
    status: str,
    started_at: str,
    report_id: str | None = None,
    completed_at: str | None = None,
    error_message: str | None = None,
    tavily_searches_used: int | None = None,
    groq_tokens_used: int | None = None,
) -> None:
    initialize_database()
    with transaction() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO run_history (
                run_id, report_id, schedule_id, started_at, completed_at, status,
                error_message, tavily_searches_used, groq_tokens_used
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                report_id,
                schedule_id,
                started_at,
                completed_at,
                status,
                error_message,
                tavily_searches_used,
                groq_tokens_used,
            ),
        )


def list_recent_run_history(limit: int = 20) -> list[dict[str, Any]]:
    initialize_database()
    with transaction() as connection:
        rows = connection.execute(
            """
            SELECT run_id, report_id, schedule_id, started_at, completed_at, status, error_message
            FROM run_history
            ORDER BY started_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
