from app.models.query import VerticalConfig


CONFIG = VerticalConfig(
    vertical_id="healthcare",
    display_name="Healthcare & HealthTech",
    search_templates=[
        "{query} healthcare competitive analysis",
        "{query} patient outcomes market share",
        "{query} partnerships hospitals providers",
        "{vertical} market leaders 2025",
    ],
    swot_framework=(
        "Focus on patient outcomes, regulatory exposure, provider network reach, reimbursement "
        "model, interoperability, and care delivery innovation."
    ),
    rss_feeds=[
        "https://www.fiercehealthcare.com/rss/xml",
        "https://www.mobihealthnews.com/rss.xml",
        "https://www.healthcareitnews.com/home/feed",
    ],
    key_metrics=["patient volume", "provider network", "reimbursement", "adoption", "retention"],
    competitor_discovery_queries=[
        "top digital health companies 2025",
        "{query} competitors healthcare",
    ],
)
