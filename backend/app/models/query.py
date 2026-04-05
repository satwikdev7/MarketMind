from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class QueryInput(BaseModel):
    query: str = Field(..., min_length=3)
    vertical: str = Field(..., min_length=2)
    target_companies: Optional[list[str]] = None
    focus_areas: Optional[list[str]] = None


class VerticalConfig(BaseModel):
    vertical_id: str
    display_name: str
    search_templates: list[str]
    swot_framework: str
    rss_feeds: list[str]
    key_metrics: list[str]
    competitor_discovery_queries: list[str]
