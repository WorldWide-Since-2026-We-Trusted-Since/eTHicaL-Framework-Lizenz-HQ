# SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
# SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
"""Minimal GLEIF Legal Entity Identifier (LEI) REST client.

GLEIF publishes the global LEI index under CC0-1.0. The LEI is the universal
key for the UECF institutional layer (banks, central banks, sovereign wealth
funds and companies). API docs: https://www.gleif.org/en/lei-data/gleif-api
"""
from __future__ import annotations

import hashlib
import urllib.parse
from pathlib import Path

from .http import cached_get_json

API_BASE = "https://api.gleif.org/api/v1"


def _record_dict(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise TypeError("GLEIF response is not an object")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise TypeError("GLEIF single-record response has no 'data' object")
    return data


def _record_list(payload: object) -> tuple[int, list[dict[str, object]]]:
    if not isinstance(payload, dict):
        raise TypeError("GLEIF response is not an object")
    data = payload.get("data")
    if not isinstance(data, list):
        raise TypeError("GLEIF list response has no 'data' array")
    meta = payload.get("meta")
    total = 0
    if isinstance(meta, dict):
        pagination = meta.get("pagination")
        if isinstance(pagination, dict) and isinstance(pagination.get("total"), int):
            total = pagination["total"]
    return total, [row for row in data if isinstance(row, dict)]


def _str_at(node: object, *path: str) -> str | None:
    current = node
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current if isinstance(current, str) else None


def summarise(record: dict[str, object]) -> dict[str, object]:
    """Reduce a raw LEI record to the fields the UECF analysis cares about."""
    attributes = record.get("attributes")
    attributes = attributes if isinstance(attributes, dict) else {}
    entity = attributes.get("entity")
    entity = entity if isinstance(entity, dict) else {}
    return {
        "lei": record.get("id") if isinstance(record.get("id"), str) else None,
        "legalName": _str_at(entity, "legalName", "name"),
        "jurisdiction": _str_at(entity, "jurisdiction"),
        "category": _str_at(entity, "category"),
        "country": _str_at(entity, "legalAddress", "country"),
        "city": _str_at(entity, "legalAddress", "city"),
        "status": _str_at(entity, "status"),
    }


def record(lei: str, cache_dir: Path, *, refresh: bool = False) -> dict[str, object]:
    url = f"{API_BASE}/lei-records/{urllib.parse.quote(lei)}"
    cache_path = cache_dir / f"gleif-lei-{lei}.json"
    return _record_dict(cached_get_json(url, cache_path, refresh=refresh))


def search_by_name(
    name: str, cache_dir: Path, *, size: int = 5, refresh: bool = False
) -> tuple[int, list[dict[str, object]]]:
    query = urllib.parse.urlencode({"filter[entity.legalName]": name, "page[size]": size})
    url = f"{API_BASE}/lei-records?{query}"
    digest = hashlib.sha1(query.encode("utf-8")).hexdigest()[:10]
    cache_path = cache_dir / f"gleif-search-{digest}.json"
    return _record_list(cached_get_json(url, cache_path, refresh=refresh))
