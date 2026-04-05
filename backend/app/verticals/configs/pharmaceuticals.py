from app.models.query import VerticalConfig


CONFIG = VerticalConfig(
    vertical_id="pharmaceuticals",
    display_name="Pharmaceuticals",
    search_templates=[
        "{query} pharmaceutical competitive analysis",
        "{query} drug pipeline competitors",
        "{query} clinical trial partnerships",
        "{vertical} market leaders 2025",
    ],
    swot_framework=(
        "Focus on drug pipeline depth, patent cliffs, clinical milestones, regulatory progress, "
        "commercialization partnerships, and manufacturing capability."
    ),
    rss_feeds=[
        "https://www.fiercepharma.com/rss/xml",
        "https://www.pharmaceutical-technology.com/feed/",
        "https://www.biopharmadive.com/feeds/news/",
    ],
    key_metrics=["pipeline size", "trial stage", "patent life", "revenue mix", "launch cadence"],
    competitor_discovery_queries=[
        "top pharma companies 2025",
        "{query} competitors drug pipeline",
    ],
)
