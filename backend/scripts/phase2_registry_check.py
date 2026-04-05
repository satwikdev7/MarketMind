from __future__ import annotations

from app.verticals.registry import (
    VerticalRegistryError,
    get_vertical_config,
    list_vertical_options,
    list_verticals,
    validate_registry,
)


def main() -> None:
    validate_registry()
    verticals = list_verticals()
    print(f"Registered verticals: {len(verticals)}")
    print(list_vertical_options())
    technology = get_vertical_config("technology")
    print(f"Technology display name: {technology.display_name}")
    try:
        get_vertical_config("unknown_vertical")
    except VerticalRegistryError as exc:
        print(f"Invalid vertical check passed: {exc}")


if __name__ == "__main__":
    main()
