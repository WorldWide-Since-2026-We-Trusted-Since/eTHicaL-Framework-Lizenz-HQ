# SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
# SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
"""OpenStreetMap Overpass API client (data licensed ODbL-1.0).

Standard library only. Overpass enforces rate limits and answers with
``HTTP 429 Too Many Requests`` (and ``504`` when overloaded); the shared
:mod:`ingest.http` layer retries those with ``Retry-After`` backoff.

Overpass has no offset/cursor paging, so we paginate **spatially**: the caller
supplies a list of bounding-box tiles, we issue one query per tile and
aggregate the elements, de-duplicated by ``(type, id)``. A polite pause is
inserted between tiles.

Dump fallback: when the live API is unreachable/rate-limited, the pipeline
falls back to the committed sample ``data/samples/osm-overpass-sample.json``
(see ``docs/DATA-LICENSES.md``).
"""
from __future__ import annotations

import time
from typing import Callable

from .http import post_form

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

#: Small default tiles (south, west, north, east) over dense European metros,
#: kept tiny so a live smoke test returns quickly and politely.
DEFAULT_TILES: tuple[tuple[float, float, float, float], ...] = (
    (52.50, 13.36, 52.53, 13.42),  # Berlin (Mitte)
    (50.10, 8.66, 50.13, 8.71),    # Frankfurt (near DE-CIX)
)


def build_query(osm_tag: str, bbox: tuple[float, float, float, float], *, timeout: int = 60) -> str:
    """Build an Overpass QL query for nodes carrying ``osm_tag`` within ``bbox``."""
    south, west, north, east = bbox
    return (
        f"[out:json][timeout:{timeout}];"
        f"node[{osm_tag}]({south},{west},{north},{east});"
        f"out body;"
    )


def elements(payload: object) -> list[dict[str, object]]:
    """Extract the ``elements`` array from a raw Overpass JSON payload."""
    if not isinstance(payload, dict):
        raise TypeError("Overpass response is not an object")
    items = payload.get("elements")
    if not isinstance(items, list):
        raise TypeError("Overpass response has no 'elements' array")
    return [el for el in items if isinstance(el, dict)]


def fetch_bbox(osm_tag: str, bbox: tuple[float, float, float, float], **kwargs: object) -> list[dict[str, object]]:
    """Fetch all nodes tagged ``osm_tag`` inside a single bounding box."""
    query = build_query(osm_tag, bbox)
    payload = post_form(OVERPASS_URL, {"data": query}, **kwargs)  # type: ignore[arg-type]
    return elements(payload)


def paginate_tiles(
    osm_tag: str,
    tiles: tuple[tuple[float, float, float, float], ...] = DEFAULT_TILES,
    *,
    pause: float = 1.0,
    sleep: Callable[[float], None] = time.sleep,
    **kwargs: object,
) -> list[dict[str, object]]:
    """Spatial pagination: query each tile and aggregate de-duplicated nodes."""
    seen: dict[tuple[object, object], dict[str, object]] = {}
    for index, bbox in enumerate(tiles):
        for element in fetch_bbox(osm_tag, bbox, **kwargs):
            seen[(element.get("type"), element.get("id"))] = element
        if index < len(tiles) - 1:
            sleep(pause)  # be polite to the shared Overpass instance
    return list(seen.values())


def summarise(elements: list[dict[str, object]]) -> dict[str, object]:
    """Reduce raw Overpass nodes to the counts the UECF analysis cares about."""
    named = 0
    for element in elements:
        tags = element.get("tags")
        if isinstance(tags, dict) and tags.get("name"):
            named += 1
    return {"count": len(elements), "with_name": named}
