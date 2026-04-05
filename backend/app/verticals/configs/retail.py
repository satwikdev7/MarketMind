from app.models.query import VerticalConfig


CONFIG = VerticalConfig(
    vertical_id="retail",
    display_name="Retail & Commerce",
    search_templates=[
        "{query} retail competitive analysis",
        "{query} ecommerce market share",
        "{query} pricing strategy competitors",
        "{vertical} market leaders ranking",
    ],
    swot_framework=(
        "Focus on channel mix, pricing power, merchandising, customer acquisition, fulfillment, "
        "brand strength, and omnichannel execution."
    ),
    rss_feeds=[
        "https://www.retaildive.com/feeds/news/",
        "https://www.digitalcommerce360.com/feed/",
        "https://chainstoreage.com/rss.xml",
    ],
    key_metrics=["same-store sales", "AOV", "conversion rate", "repeat purchase", "gross margin"],
    competitor_discovery_queries=[
        "top retail companies 2025",
        "{query} competitors ecommerce",
    ],
)
