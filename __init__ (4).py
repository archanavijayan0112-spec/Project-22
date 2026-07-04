import json
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@lru_cache
def get_grid_intensity() -> dict:
    with open(DATA_DIR / "grid_intensity.json") as f:
        return json.load(f)


@lru_cache
def get_instance_power() -> dict:
    with open(DATA_DIR / "instance_power.json") as f:
        return json.load(f)


def region_intensity(provider: str, region: str) -> float:
    """Return gCO2eq/kWh for a given provider + region, raising if unknown."""
    data = get_grid_intensity()
    try:
        return data[provider][region]
    except KeyError as exc:
        raise ValueError(f"Unknown region '{region}' for provider '{provider}'") from exc


def all_regions(provider: str) -> dict:
    return get_grid_intensity().get(provider, {})
