from app.models.query import VerticalConfig


CONFIG = VerticalConfig(
    vertical_id="real_estate",
    display_name="Real Estate & PropTech",
    search_templates=[
        "{query} proptech competitive analysis",
        "{query} real estate market share competitors",
        "{query} property management partnerships",
        "{vertical} market leaders 2025",
    ],
    swot_framework=(
        "Focus on occupancy, transaction velocity, property coverage, unit economics, platform "
        "stickiness, regulatory constraints, and financing exposure."
    ),
    rss_feeds=[
        "https://www.housingwire.com/rss/",
        "https://therealdeal.com/feed/",
        "https://www.propmodo.com/feed/",
    ],
    key_metrics=["occupancy", "GMV", "units managed", "transaction volume", "CAC"],
    competitor_discovery_queries=[
        "top proptech companies 2025",
        "{query} competitors real estate",
    ],
)
