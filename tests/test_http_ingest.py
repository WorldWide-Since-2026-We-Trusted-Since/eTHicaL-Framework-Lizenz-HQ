# SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
# SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
"""Deterministic, offline tests for HTTP rate-limit handling + OSM/Wikidata.

No real network is used: the ``opener`` and ``sleep`` seams of ``ingest.http``
are injected with fakes so HTTP 429 retry/backoff is exercised without sockets
or real waiting.
"""
from __future__ import annotations

import email.message
import io
import json
import urllib.error
from pathlib import Path

import pytest

from ingest import http, osm, wikidata

URL = "https://example.test/api"
SAMPLES = Path(__file__).resolve().parent.parent / "data" / "samples"


class _FakeResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body
        self.closed = False

    def read(self) -> bytes:
        return self._body

    def close(self) -> None:
        self.closed = True


def _http_error(code: int, *, retry_after: object = None, body: bytes = b"err") -> urllib.error.HTTPError:
    headers = email.message.Message()
    if retry_after is not None:
        headers["Retry-After"] = str(retry_after)
    return urllib.error.HTTPError(URL, code, "error", headers, io.BytesIO(body))


def _opener(actions: list[object]):
    """Return an opener that replays ``actions`` (bytes => body, Exception => raise)."""
    seq = iter(actions)

    def opener(request: object, timeout: int) -> _FakeResponse:
        action = next(seq)
        if isinstance(action, Exception):
            raise action
        assert isinstance(action, (bytes, bytearray))
        return _FakeResponse(bytes(action))

    return opener


# --- HTTP 429 / rate limiting -------------------------------------------------

def test_get_json_retries_after_429_then_succeeds() -> None:
    sleeps: list[float] = []
    opener = _opener([_http_error(429, retry_after=0), b'{"ok": true}'])
    result = http.get_json(URL, opener=opener, sleep=sleeps.append, backoff=0.01)
    assert result == {"ok": True}
    assert len(sleeps) == 1  # retried exactly once


def test_get_json_honours_retry_after_header() -> None:
    sleeps: list[float] = []
    opener = _opener([_http_error(429, retry_after=2), b"{}"])
    http.get_json(URL, opener=opener, sleep=sleeps.append)
    assert sleeps == [2.0]


def test_get_json_raises_rate_limit_error_after_exhausting_retries() -> None:
    opener = _opener([_http_error(429, retry_after=0) for _ in range(5)])
    with pytest.raises(http.RateLimitError):
        http.get_json(URL, opener=opener, sleep=lambda _s: None, retries=4)


def test_non_retryable_http_error_raises_immediately() -> None:
    calls: list[float] = []
    opener = _opener([_http_error(404)])
    with pytest.raises(http.HttpError):
        http.get_json(URL, opener=opener, sleep=calls.append)
    assert calls == []  # 404 is not retried


# --- OSM Overpass client ------------------------------------------------------

def test_osm_build_query_is_overpass_ql() -> None:
    query = osm.build_query("telecom=data_center", (1.0, 2.0, 3.0, 4.0))
    assert "[out:json]" in query
    assert "node[telecom=data_center](1.0,2.0,3.0,4.0)" in query


def test_osm_paginate_tiles_deduplicates_and_summarises() -> None:
    tile_a = json.dumps({"elements": [{"type": "node", "id": 1, "tags": {"name": "DE-CIX"}}]}).encode()
    tile_b = json.dumps(
        {"elements": [{"type": "node", "id": 1, "tags": {"name": "DE-CIX"}}, {"type": "node", "id": 2}]}
    ).encode()
    nodes = osm.paginate_tiles(
        "telecom=data_center",
        ((0, 0, 1, 1), (1, 1, 2, 2)),
        pause=0,
        sleep=lambda _s: None,
        opener=_opener([tile_a, tile_b]),
    )
    assert {n["id"] for n in nodes} == {1, 2}  # id 1 de-duplicated across tiles
    assert osm.summarise(nodes) == {"count": 2, "with_name": 1}


def test_osm_rejects_malformed_payload() -> None:
    with pytest.raises(TypeError):
        osm.elements({"no_elements": []})


# --- Wikidata SPARQL client ---------------------------------------------------

def test_wikidata_run_query_and_summarise() -> None:
    page = {
        "results": {
            "bindings": [
                {
                    "item": {"type": "uri", "value": "http://www.wikidata.org/entity/Q1"},
                    "itemLabel": {"type": "literal", "value": "Example"},
                    "lei": {"type": "literal", "value": "L1"},
                }
            ]
        }
    }
    rows = wikidata.run_query("SELECT ?item WHERE {}", opener=_opener([json.dumps(page).encode()]))
    assert wikidata.summarise(rows) == [
        {"item": "http://www.wikidata.org/entity/Q1", "label": "Example", "lei": "L1"}
    ]


def test_wikidata_paginate_stops_on_short_page() -> None:
    full = {"results": {"bindings": [{"item": {"value": "Q1"}}, {"item": {"value": "Q2"}}]}}
    short = {"results": {"bindings": [{"item": {"value": "Q3"}}]}}
    rows = wikidata.paginate(
        "SELECT ?item WHERE {}",
        page_size=2,
        max_pages=5,
        pause=0,
        sleep=lambda _s: None,
        opener=_opener([json.dumps(full).encode(), json.dumps(short).encode()]),
    )
    assert len(rows) == 3  # stopped after the short second page


# --- Committed dump fallbacks stay parseable ----------------------------------

def test_committed_dump_samples_parse() -> None:
    osm_sample = json.loads((SAMPLES / "osm-overpass-sample.json").read_text(encoding="utf-8"))
    assert osm.summarise(osm.elements(osm_sample))["count"] == 3
    wd_sample = json.loads((SAMPLES / "wikidata-lei-sample.json").read_text(encoding="utf-8"))
    summary = wikidata.summarise(wikidata.bindings(wd_sample))
    assert len(summary) == 3
    assert all(row["lei"] for row in summary)
