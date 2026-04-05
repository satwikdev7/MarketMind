from app.models.query import VerticalConfig


CONFIG = VerticalConfig(
    vertical_id="saas",
    display_name="SaaS",
    search_templates=[
        "{query} saas competitive analysis",
        "{query} pricing competitors",
        "{query} product launch announcement",
        "{vertical} market leaders ranking",
    ],
    swot_framework=(
        "Focus on product-led growth, pricing tiers, retention, ecosystem, onboarding friction, "
        "AI differentiation, and enterprise expansion motion."
    ),
    rss_feeds=[
        "https://www.saastr.com/feed/",
        "https://techcrunch.com/feed/",
        "https://www.productledalliance.com/blog/rss/",
    ],
    key_metrics=["ARR", "NRR", "logo retention", "ACV", "payback period"],
    competitor_discovery_queries=[
        "top SaaS companies 2025",
        "alternatives to {query} saas",
    ],
)
