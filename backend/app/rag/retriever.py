from __future__ import annotations

from typing import Any

from app.config import get_settings
from app.rag.embeddings import embed_query
from app.rag.vector_store import get_or_create_collection


def retrieve_relevant_chunks(
    query: str,
    vertical: str,
    top_k: int | None = None,
    metadata_filter: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    settings = get_settings()
    collection = get_or_create_collection(vertical)
    results = collection.query(
        query_embeddings=[embed_query(query)],
        n_results=top_k or settings.rag_top_k,
        where=metadata_filter,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    return [
        {
            "content": document,
            "metadata": metadata or {},
            "distance": distance,
        }
        for document, metadata, distance in zip(documents, metadatas, distances)
    ]
