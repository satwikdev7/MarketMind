from __future__ import annotations

import re
from urllib.parse import urlparse


WHITESPACE_RE = re.compile(r"\s+")


def normalize_whitespace(text: str) -> str:
    return WHITESPACE_RE.sub(" ", text).strip()


def truncate_text(text: str, max_length: int) -> str:
    cleaned = normalize_whitespace(text)
    if len(cleaned) <= max_length:
        return cleaned
    return cleaned[: max(0, max_length - 3)].rstrip() + "..."


def extract_domain(url: str) -> str:
    return urlparse(url).netloc.lower()


def deduplicate_urls(urls: list[str]) -> list[str]:
    seen: set[str] = set()
    unique_urls: list[str] = []
    for url in urls:
        normalized = url.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique_urls.append(normalized)
    return unique_urls
