from app.models.query import VerticalConfig


CONFIG = VerticalConfig(
    vertical_id="energy",
    display_name="Energy",
    search_templates=[
        "{query} energy competitive analysis",
        "{query} project pipeline competitors",
        "{query} partnerships utilities",
        "{vertical} market leaders 2025",
    ],
    swot_framework=(
        "Focus on generation mix, project pipeline, regulatory support, grid integration, capital "
        "intensity, and supply chain resilience."
    ),
    rss_feeds=[
        "https://www.utilitydive.com/feeds/news/",
        "https://www.energy-storage.news/feed/",
        "https://www.greentechmedia.com/rss",
    ],
    key_metrics=["MW deployed", "pipeline", "capacity factor", "PPA volume", "cost per MWh"],
    competitor_discovery_queries=[
        "top energy companies 2025",
        "{query} competitors renewables",
    ],
)
