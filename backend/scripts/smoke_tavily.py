from __future__ import annotations

from app.config import get_settings


def main() -> None:
    settings = get_settings()
    if not settings.tavily_api_key:
        raise RuntimeError("TAVILY_API_KEY is missing in backend/.env")

    try:
        from tavily import TavilyClient
    except ImportError as exc:
        raise RuntimeError("tavily-python is not installed") from exc

    client = TavilyClient(api_key=settings.tavily_api_key)
    response = client.search(
        query="latest competitive intelligence trends",
        max_results=3,
        search_depth="basic",
    )
    results = response.get("results", [])
    print(f"Returned {len(results)} results")
    if results:
        print(results[0].get("title", "No title"))


if __name__ == "__main__":
    main()
