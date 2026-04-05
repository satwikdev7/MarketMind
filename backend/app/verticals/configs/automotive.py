from app.models.query import VerticalConfig


CONFIG = VerticalConfig(
    vertical_id="automotive",
    display_name="Automotive & Mobility",
    search_templates=[
        "{query} automotive competitive analysis",
        "{query} EV market share competitors",
        "{query} autonomous driving partnerships",
        "{vertical} market leaders 2025",
    ],
    swot_framework=(
        "Focus on manufacturing scale, battery supply chain, autonomy roadmap, dealer/distribution "
        "strategy, software differentiation, and capital efficiency."
    ),
    rss_feeds=[
        "https://electrek.co/feed/",
        "https://www.autonews.com/rss.xml",
        "https://insideevs.com/rss/news/",
    ],
    key_metrics=["vehicle deliveries", "battery capacity", "gross margin", "software revenue", "fleet size"],
    competitor_discovery_queries=[
        "top EV companies 2025",
        "{query} competitors mobility",
    ],
)
