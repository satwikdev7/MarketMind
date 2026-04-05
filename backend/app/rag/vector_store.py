from __future__ import annotations

from functools import lru_cache
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection

from app.config import get_settings
from app.models.research import RAGDocument, ResearchBundle
from app.rag.chunker import ChunkingContext, chunk_scraped_content
from app.rag.embeddings import embed_texts


@lru_cache(maxsize=1)
def get_chroma_client() -> chromadb.PersistentClient:
    settings = get_settings()
    return chromadb.PersistentClient(path=str(settings.chroma_dir))


def get_collection_name(vertical: str) -> str:
    return f"marketmind_{vertical}"


def get_or_create_collection(vertical: str) -> Collection:
    client = get_chroma_client()
    return client.get_or_create_collection(name=get_collection_name(vertical))


def upsert_documents(vertical: str, documents: list[RAGDocument]) -> int:
    if not documents:
        return 0

    collection = get_or_create_collection(vertical)
    embeddings = embed_texts([document.content for document in documents])
    collection.upsert(
        ids=[document.doc_id for document in documents],
        documents=[document.content for document in documents],
        metadatas=[_sanitize_metadata(document.metadata) for document in documents],
        embeddings=embeddings,
    )
    return len(documents)


def ingest_research_bundle(bundle: ResearchBundle) -> int:
    result_by_url = {result.url: result for result in bundle.search_results}
    all_documents: list[RAGDocument] = []

    for scraped in bundle.scraped_content:
        if not scraped.scrape_success or not scraped.content:
            continue
        context = ChunkingContext(vertical=bundle.vertical, search_result=result_by_url.get(scraped.url))
        all_documents.extend(chunk_scraped_content(scraped, context=context))

    return upsert_documents(bundle.vertical, all_documents)


def collection_stats(vertical: str) -> dict[str, Any]:
    collection = get_or_create_collection(vertical)
    payload = collection.get(include=["metadatas"], limit=1000)
    metadatas = payload.get("metadatas", [])
    return {
        "collection_name": get_collection_name(vertical),
        "document_count": collection.count(),
        "sample_metadata_count": len(metadatas),
    }


def _sanitize_metadata(metadata: dict[str, Any]) -> dict[str, str | int | float | bool]:
    sanitized: dict[str, str | int | float | bool] = {}
    for key, value in metadata.items():
        if value is None:
            continue
        if isinstance(value, (str, int, float, bool)):
            sanitized[key] = value
        else:
            sanitized[key] = str(value)
    return sanitized
