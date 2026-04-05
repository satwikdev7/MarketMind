from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.models.analysis import CompetitorProfile, CompetitiveSignal, SWOTAnalysis


class ReportSection(BaseModel):
    title: str
    content: str
    order: int


class IntelligenceReport(BaseModel):
    report_id: str
    query: str
    vertical: str
    generated_at: str
    executive_summary: str
    competitor_profiles: list[CompetitorProfile]
    swot_analysis: SWOTAnalysis
    competitive_signals: list[CompetitiveSignal]
    key_trends: list[str]
    strategic_recommendations: list[str]
    sources_cited: list[str]
    total_sources_searched: int = Field(ge=0)
    generation_time_sec: float = Field(ge=0.0)
    llm_calls_made: int = Field(ge=0)
    sections: list[ReportSection]


class ScheduledReport(BaseModel):
    schedule_id: str
    query: str
    vertical: str
    cron_expression: Optional[str] = None
    interval_hours: Optional[int] = None
    is_active: bool = True
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    created_at: str
