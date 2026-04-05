from app.models.query import VerticalConfig


CONFIG = VerticalConfig(
    vertical_id="logistics",
    display_name="Logistics & Supply Chain",
    search_templates=[
        "{query} logistics competitive analysis",
        "{query} freight market share competitors",
        "{query} supply chain partnerships",
        "{vertical} market leaders 2025",
    ],
    swot_framework=(
        "Focus on delivery speed, network density, route optimization, gross margin, warehouse "
        "footprint, cross-border capability, and automation."
    ),
    rss_feeds=[
        "https://www.supplychaindive.com/feeds/news/",
        "https://www.freightwaves.com/news/feed",
        "https://www.logisticsmgmt.com/rss",
    ],
    key_metrics=["on-time delivery", "network density", "cost per shipment", "warehouse footprint", "turnover"],
    competitor_discovery_queries=[
        "top logistics companies 2025",
        "{query} competitors supply chain",
    ],
)
