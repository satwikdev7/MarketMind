from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Iterable
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

from app.config import get_settings
from app.models.research import ScrapedContent, SearchResult
from app.utils.text_utils import normalize_whitespace, truncate_text


MAX_CONCURRENT_SCRAPES = 5


async def scrape_search_results(results: Iterable[SearchResult], limit: int = 5) -> list[ScrapedContent]:
    selected_results = list(results)[:limit]
    if not selected_results:
        return []

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_SCRAPES)
    domain_locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
    async with httpx.AsyncClient(
        timeout=get_settings().scrape_timeout_sec,
        headers={"User-Agent": get_settings().scrape_user_agent},
        follow_redirects=True,
    ) as client:
        tasks = [
            _scrape_one(result=result, client=client, semaphore=semaphore, domain_locks=domain_locks)
            for result in selected_results
        ]
        return await asyncio.gather(*tasks)


async def _scrape_one(
    result: SearchResult,
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    domain_locks: dict[str, asyncio.Lock],
) -> ScrapedContent:
    domain = urlparse(result.url).netloc
    async with semaphore:
        if not _is_allowed_by_robots(result.url):
            return ScrapedContent(
                url=result.url,
                title=result.title,
                content="",
                content_length=0,
                scrape_success=False,
                error="Blocked by robots.txt",
            )

        async with domain_locks[domain]:
            await asyncio.sleep(1)
            try:
                response = await client.get(result.url)
                response.raise_for_status()
            except Exception as exc:
                return ScrapedContent(
                    url=result.url,
                    title=result.title,
                    content="",
                    content_length=0,
                    scrape_success=False,
                    error=str(exc),
                )

    extracted = _extract_main_text(response.text)
    content = truncate_text(extracted, get_settings().scrape_max_content_length)
    return ScrapedContent(
        url=result.url,
        title=result.title,
        content=content,
        content_length=len(content),
        scrape_success=bool(content),
        error=None if content else "No article content extracted",
    )


def _extract_main_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()

    main_node = soup.find("article") or soup.find("main") or soup.body or soup
    text = main_node.get_text(separator=" ", strip=True)
    return normalize_whitespace(text)


def _is_allowed_by_robots(url: str) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    parser = RobotFileParser()
    try:
        parser.set_url(robots_url)
        parser.read()
        return parser.can_fetch(get_settings().scrape_user_agent, url)
    except Exception:
        return True
