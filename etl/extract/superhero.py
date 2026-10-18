"""SuperHero API (akabab, JSON estático no jsDelivr): powerstats e biografia."""
from __future__ import annotations

from .http import get_json

URL = "https://cdn.jsdelivr.net/gh/akabab/superhero-api@0.3.0/api/all.json"


def todos() -> list[dict]:
    return get_json(URL)


def por_id() -> dict[int, dict]:
    return {h["id"]: h for h in todos()}
