# SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
# SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
"""Wikidata Query Service (SPARQL) client (data licensed CC0-1.0).

Standard library only. The Wikidata Query Service rate-limits clients and
returns ``HTTP 429 Too Many Requests``; the shared :mod:`ingest.http` layer
retries with ``Retry-After`` backoff. A descriptive ``User-Agent`` is required
by the Wikimedia user-agent policy and is set centrally in ``ingest.http``.

Pagination uses SPARQL ``LIMIT``/``OFFSET``: we keep requesting pages until a
short page signals the end. The default query selects entities that carry a
GLEIF **Legal Entity Identifier** (property ``P1278``), tying Wikidata directly
into the UECF institutional layer (the LEI is the universal entity key).

Dump fallback: when the live endpoint is unreachable/rate-limited, the pipeline
falls back to the committed sample ``data/samples/wikidata-lei-sample.json``
(see ``docs/DATA-LICENSES.md``).
"""
from __future__ import annotations

import time
import urllib.parse
from typing import Callable

from .http import get_json

SPARQL_URL = "https://query.wikidata.org/sparql"

#: Entities that carry a GLEIF LEI (P1278) — the bridge to the GLEIF source.
ENTITIES_WITH_LEI = """SELECT ?item ?itemLabel ?lei WHERE {
  ?item wdt:P1278 ?lei .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,de". }
}"""


def bindings(payload: object) -> list[dict[str, object]]:
    """Extract the solution ``bindings`` from a raw SPARQL JSON payload."""
    if not isinstance(payload, dict):
        raise TypeError("Wikidata SPARQL response is not an object")
    results = payload.get("results")
    if not isinstance(results, dict):
        raise TypeError("Wikidata SPARQL response has no 'results' object")
    rows = results.get("bindings")
    if not isinstance(rows, list):
        raise TypeError("Wikidata SPARQL response has no 'bindings' array")
    return [row for row in rows if isinstance(row, dict)]


def run_query(sparql: str, **kwargs: object) -> list[dict[str, object]]:
    """Execute a SPARQL query and return its solution bindings."""
    query = urllib.parse.urlencode({"query": sparql, "format": "json"})
    url = f"{SPARQL_URL}?{query}"
    return bindings(get_json(url, **kwargs))  # type: ignore[arg-type]


def paginate(
    sparql_body: str,
    *,
    order_by: str = "?item",
    page_size: int = 200,
    max_pages: int = 10,
    pause: float = 1.0,
    sleep: Callable[[float], None] = time.sleep,
    **kwargs: object,
) -> list[dict[str, object]]:
    """Page through a SPARQL query via LIMIT/OFFSET until a short page."""
    rows: list[dict[str, object]] = []
    for page in range(max_pages):
        paged = f"{sparql_body}\nORDER BY {order_by}\nLIMIT {page_size}\nOFFSET {page * page_size}"
        batch = run_query(paged, **kwargs)
        rows.extend(batch)
        if len(batch) < page_size:
            break
        sleep(pause)
    return rows


def _value(row: dict[str, object], key: str) -> str | None:
    cell = row.get(key)
    if isinstance(cell, dict) and isinstance(cell.get("value"), str):
        return cell["value"]
    return None


def summarise(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Reduce SPARQL bindings to ``{item, label, lei}`` triples."""
    return [
        {"item": _value(r, "item"), "label": _value(r, "itemLabel"), "lei": _value(r, "lei")}
        for r in rows
    ]


def entities_with_lei(**kwargs: object) -> list[dict[str, object]]:
    """Fetch (paginated) Wikidata entities that carry a GLEIF LEI."""
    return paginate(ENTITIES_WITH_LEI, order_by="?item", **kwargs)
