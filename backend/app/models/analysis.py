from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class CompetitorProfile(BaseModel):
    name: str
    description: str
    market_position: str
    strengths: list[str]
    weaknesses: list[str]
    recent_moves: list[str]
    source_urls: list[str]


class CompetitiveSignal(BaseModel):
    signal_type: str
    company: str
    description: str
    date: Optional[str] = None
    impact: str
    source_url: str


class SWOTEntry(BaseModel):
    point: str
    supporting_evidence: str
    source_url: Optional[str] = None


class SWOTAnalysis(BaseModel):
    target: str
    strengths: list[SWOTEntry]
    weaknesses: list[SWOTEntry]
    opportunities: list[SWOTEntry]
    threats: list[SWOTEntry]


class AnalysisResult(BaseModel):
    competitor_profiles: list[CompetitorProfile]
    competitive_signals: list[CompetitiveSignal]
    swot_analysis: SWOTAnalysis
