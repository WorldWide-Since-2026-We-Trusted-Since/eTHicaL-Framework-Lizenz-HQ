# SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
# SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
"""Minimal PeeringDB REST API client.

PeeringDB data is licensed CC-BY-4.0. Endpoints used:
``ix`` (exchanges), ``fac`` (facilities, including Equinix IBX sites),
``net`` (networks) and ``org`` (organisations).
"""
from __future__ import annotations

import hashlib
import time
import urllib.parse
from pathlib import Path

from .http import cached_get_json

API_BASE = "https://www.peeringdb.com/api"

# PeeringDB throttles unbounded anonymous list queries (limit=0). Page instead.
PAGE_SIZE = 500


def _envelope_data(payload: object) -> list[dict[str, object]]:
    if not isinstance(payload, dict):
        raise TypeError("PeeringDB response is not an object")
    data = payload.get("data")
    if not isinstance(data, list):
        raise TypeError("PeeringDB response has no 'data' array")
    return [row for row in data if isinstance(row, dict)]


def fetch(endpoint: str, params: dict[str, str | int], cache_dir: Path, *, refresh: bool = False) -> list[dict[str, object]]:
    query = urllib.parse.urlencode(params)
    url = f"{API_BASE}/{endpoint}?{query}"
    digest = hashlib.sha1(query.encode("utf-8")).hexdigest()[:10]
    cache_path = cache_dir / f"peeringdb-{endpoint}-{digest}.json"
    return _envelope_data(cached_get_json(url, cache_path, refresh=refresh))


def paginate(
    endpoint: str,
    params: dict[str, str | int],
    cache_dir: Path,
    *,
    page_size: int = PAGE_SIZE,
    max_pages: int = 20,
    refresh: bool = False,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for page in range(max_pages):
        page_params: dict[str, str | int] = {**params, "limit": page_size, "skip": page * page_size}
        batch = fetch(endpoint, page_params, cache_dir, refresh=refresh)
        rows.extend(batch)
        if len(batch) < page_size:
            break
        time.sleep(1)  # be polite to the anonymous API
    return rows


def exchanges(cache_dir: Path, *, refresh: bool = False) -> list[dict[str, object]]:
    return paginate("ix", {}, cache_dir, refresh=refresh)


def facilities(cache_dir: Path, *, name_contains: str | None = None, refresh: bool = False) -> list[dict[str, object]]:
    params: dict[str, str | int] = {}
    if name_contains:
        params["name__contains"] = name_contains
    return paginate("fac", params, cache_dir, refresh=refresh)


def equinix_ibx(cache_dir: Path, *, refresh: bool = False) -> list[dict[str, object]]:
    """Equinix IBX facilities (Axiom-relevant: physical interconnection sites)."""
    return facilities(cache_dir, name_contains="Equinix", refresh=refresh)
