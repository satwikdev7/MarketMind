from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    url: str
    title: str
    snippet: str
    source: str
    published_date: Optional[str] = None
    relevance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    fetched_at: str


class ScrapedContent(BaseModel):
    url: str
    title: str
    content: str
    content_length: int = Field(ge=0)
    scrape_success: bool
    error: Optional[str] = None


class RAGDocument(BaseModel):
    doc_id: str
    content: str
    metadata: dict[str, Any]
    embedding: Optional[list[float]] = None


class ResearchBundle(BaseModel):
    query: str
    vertical: str
    search_results: list[SearchResult]
    scraped_content: list[ScrapedContent]
    total_sources: int = Field(ge=0)
    unique_domains: int = Field(ge=0)
    quality_score: float = Field(ge=0.0, le=1.0)
