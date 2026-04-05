from app.models.query import VerticalConfig


CONFIG = VerticalConfig(
    vertical_id="finance",
    display_name="Finance & FinTech",
    search_templates=[
        "{query} fintech competitive analysis",
        "{query} funding valuation competitors",
        "{query} banking partnerships",
        "{vertical} market leaders 2025",
    ],
    swot_framework=(
        "Focus on regulatory exposure, trust, unit economics, product breadth, banking "
        "partnerships, fraud prevention, and monetization."
    ),
    rss_feeds=[
        "https://fintechnews.ch/feed/",
        "https://www.paymentsdive.com/feeds/news/",
        "https://www.americanbanker.com/feeds/all.rss",
    ],
    key_metrics=["AUM", "TPV", "take rate", "customer growth", "net revenue"],
    competitor_discovery_queries=[
        "top fintech companies 2025",
        "alternatives to {query} fintech",
    ],
)
