from __future__ import annotations

import hashlib
from dataclasses import dataclass

from app.config import get_settings
from app.models.research import RAGDocument, ScrapedContent, SearchResult
from app.utils.text_utils import normalize_whitespace


@dataclass(frozen=True)
class ChunkingContext:
    vertical: str
    search_result: SearchResult | None = None


def chunk_scraped_content(
    scraped_content: ScrapedContent,
    context: ChunkingContext,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[RAGDocument]:
    settings = get_settings()
    max_chunk_size = chunk_size or settings.rag_chunk_size
    overlap = chunk_overlap or settings.rag_chunk_overlap

    normalized_content = normalize_whitespace(scraped_content.content)
    if not normalized_content:
        return []

    chunks = _split_text(normalized_content, max_chunk_size=max_chunk_size, overlap=overlap)
    documents: list[RAGDocument] = []
    for index, chunk in enumerate(chunks):
        doc_id = _build_chunk_id(scraped_content.url, index, chunk)
        metadata = {
            "url": scraped_content.url,
            "title": scraped_content.title,
            "vertical": context.vertical,
            "source": context.search_result.source if context.search_result else "scraper",
            "published_date": context.search_result.published_date if context.search_result else None,
            "fetched_at": context.search_result.fetched_at if context.search_result else None,
            "chunk_index": index,
        }
        documents.append(RAGDocument(doc_id=doc_id, content=chunk, metadata=metadata))

    return documents


def _split_text(text: str, max_chunk_size: int, overlap: int) -> list[str]:
    if len(text) <= max_chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    step = max(max_chunk_size - overlap, 1)
    while start < len(text):
        end = min(start + max_chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start += step
    return chunks


def _build_chunk_id(url: str, chunk_index: int, chunk_text: str) -> str:
    digest = hashlib.sha1(f"{url}|{chunk_index}|{chunk_text}".encode("utf-8")).hexdigest()
    return digest
