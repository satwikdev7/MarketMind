from __future__ import annotations

from app.models.query import VerticalConfig
from app.verticals.configs import (
    automotive,
    energy,
    finance,
    healthcare,
    logistics,
    pharmaceuticals,
    real_estate,
    retail,
    saas,
    technology,
    telecommunications,
)


class VerticalRegistryError(ValueError):
    """Raised when a vertical config is invalid or missing."""


_REGISTRY: dict[str, VerticalConfig] = {
    config.vertical_id: config
    for config in [
        technology.CONFIG,
        healthcare.CONFIG,
        finance.CONFIG,
        retail.CONFIG,
        energy.CONFIG,
        automotive.CONFIG,
        telecommunications.CONFIG,
        pharmaceuticals.CONFIG,
        real_estate.CONFIG,
        logistics.CONFIG,
        saas.CONFIG,
    ]
}


def validate_vertical_config(config: VerticalConfig) -> None:
    if not config.search_templates:
        raise VerticalRegistryError(f"{config.vertical_id} is missing search templates")
    if not config.rss_feeds:
        raise VerticalRegistryError(f"{config.vertical_id} is missing RSS feeds")
    if not config.key_metrics:
        raise VerticalRegistryError(f"{config.vertical_id} is missing key metrics")
    if any(not template.strip() for template in config.search_templates):
        raise VerticalRegistryError(f"{config.vertical_id} contains an empty search template")
    if any(not feed.startswith(("http://", "https://")) for feed in config.rss_feeds):
        raise VerticalRegistryError(f"{config.vertical_id} contains an invalid RSS feed URL")
    if any(not metric.strip() for metric in config.key_metrics):
        raise VerticalRegistryError(f"{config.vertical_id} contains an empty key metric")


def validate_registry() -> None:
    for config in _REGISTRY.values():
        validate_vertical_config(config)


def get_vertical_config(vertical_id: str) -> VerticalConfig:
    try:
        config = _REGISTRY[vertical_id]
    except KeyError as exc:
        valid = ", ".join(sorted(_REGISTRY))
        raise VerticalRegistryError(
            f"Unknown vertical '{vertical_id}'. Expected one of: {valid}"
        ) from exc
    validate_vertical_config(config)
    return config


def list_verticals() -> list[VerticalConfig]:
    validate_registry()
    return sorted(_REGISTRY.values(), key=lambda config: config.display_name)


def list_vertical_options() -> list[tuple[str, str]]:
    return [(config.vertical_id, config.display_name) for config in list_verticals()]
