from __future__ import annotations

from app.config import get_settings


def main() -> None:
    settings = get_settings()
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is missing in backend/.env")

    try:
        from langchain_groq import ChatGroq
    except ImportError as exc:
        raise RuntimeError("langchain-groq is not installed") from exc

    llm = ChatGroq(
        model=settings.llm_secondary_model,
        api_key=settings.groq_api_key,
        temperature=0.0,
        max_tokens=32,
    )
    response = llm.invoke("Reply with exactly: MarketMind Groq OK")
    print(response.content)


if __name__ == "__main__":
    main()
