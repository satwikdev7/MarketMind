from app.models.query import VerticalConfig


CONFIG = VerticalConfig(
    vertical_id="technology",
    display_name="Technology & Software",
    search_templates=[
        "{query} competitive analysis 2025",
        "{query} market share revenue",
        "{query} vs competitors",
        "{vertical} market leaders ranking",
        "{query} product launch announcement",
    ],
    swot_framework=(
        "Focus on developer ecosystem, API capabilities, pricing model, enterprise versus SMB "
        "positioning, cloud dependencies, open-source alternatives, and AI/ML integration depth."
    ),
    rss_feeds=[
        "https://techcrunch.com/feed/",
        "https://venturebeat.com/feed/",
        "https://feeds.arstechnica.com/arstechnica/index",
    ],
    key_metrics=["ARR", "market share", "customer count", "NRR", "CAC"],
    competitor_discovery_queries=[
        "top technology companies 2025",
        "alternatives to {query}",
    ],
)
