from app.models.query import VerticalConfig


CONFIG = VerticalConfig(
    vertical_id="telecommunications",
    display_name="Telecommunications",
    search_templates=[
        "{query} telecom competitive analysis",
        "{query} subscriber growth competitors",
        "{query} 5G network expansion partnerships",
        "{vertical} market leaders 2025",
    ],
    swot_framework=(
        "Focus on subscriber growth, ARPU, network quality, spectrum assets, infrastructure "
        "investment, bundling, and enterprise connectivity."
    ),
    rss_feeds=[
        "https://www.fierce-network.com/rss/xml",
        "https://www.lightreading.com/rss_simple.asp",
        "https://telecoms.com/feed/",
    ],
    key_metrics=["ARPU", "subscriber growth", "churn", "coverage", "enterprise contracts"],
    competitor_discovery_queries=[
        "top telecom companies 2025",
        "{query} competitors 5g",
    ],
)
