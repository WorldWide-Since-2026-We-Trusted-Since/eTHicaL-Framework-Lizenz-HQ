# SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
# SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
"""Tiny HTTP helper with on-disk JSON caching (standard library only).

All requests share a single retry layer that honours HTTP rate limiting: a
``429 Too Many Requests`` (and the transient ``502/503/504`` family) is retried
with exponential backoff, respecting the ``Retry-After`` header when present.
When the retry budget is exhausted on a 429, a :class:`RateLimitError` is
raised so callers can degrade gracefully.

The network primitive (``opener``) and the ``sleep`` function are injectable so
the backoff behaviour can be tested deterministically without real sockets or
real waiting.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Callable

USER_AGENT = "uecf-poc/1.0 (+https://github.com/EU-UNION-AI-PACT/uecf-poc)"
DEFAULT_TIMEOUT = 30

#: HTTP statuses that warrant a retry. 429 is the canonical rate-limit signal.
RETRY_STATUSES = frozenset({429, 502, 503, 504})
DEFAULT_RETRIES = 4
DEFAULT_BACKOFF = 1.0
MAX_BACKOFF = 30.0

Opener = Callable[[urllib.request.Request, int], object]


class HttpError(RuntimeError):
    """Raised when a request fails or returns a non-2xx status."""


class RateLimitError(HttpError):
    """Raised when a request keeps hitting HTTP 429 after exhausting retries."""


def _default_opener(request: urllib.request.Request, timeout: int) -> object:
    return urllib.request.urlopen(request, timeout=timeout)


def _retry_after_seconds(headers: object, attempt: int, backoff: float) -> float:
    """Seconds to wait before the next attempt (Retry-After or exponential)."""
    value = headers.get("Retry-After") if hasattr(headers, "get") else None
    if value:
        try:
            return min(float(value), MAX_BACKOFF)
        except (TypeError, ValueError):
            # HTTP-date form is not parsed here; fall back to backoff.
            pass
    return min(backoff * (2 ** attempt), MAX_BACKOFF)


def _read(
    request: urllib.request.Request,
    *,
    timeout: int,
    retries: int,
    backoff: float,
    opener: Opener,
    sleep: Callable[[float], None],
) -> bytes:
    method = request.get_method()
    url = request.full_url
    for attempt in range(retries + 1):
        try:
            response = opener(request, timeout)
            try:
                return response.read()
            finally:
                close = getattr(response, "close", None)
                if callable(close):
                    close()
        except urllib.error.HTTPError as exc:
            if exc.code in RETRY_STATUSES and attempt < retries:
                sleep(_retry_after_seconds(exc.headers, attempt, backoff))
                continue
            if exc.code == 429:
                raise RateLimitError(
                    f"{method} {url} rate-limited (HTTP 429) after {attempt + 1} attempts: {exc}"
                ) from exc
            raise HttpError(f"{method} {url} failed: {exc}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt < retries:
                sleep(min(backoff * (2 ** attempt), MAX_BACKOFF))
                continue
            raise HttpError(f"{method} {url} failed: {exc}") from exc
    raise HttpError(f"{method} {url} failed: retries exhausted")  # pragma: no cover


def _decode_json(payload: bytes, method: str, url: str) -> object:
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise HttpError(f"{method} {url} returned invalid JSON: {exc}") from exc


def get_json(
    url: str,
    *,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    backoff: float = DEFAULT_BACKOFF,
    opener: Opener = _default_opener,
    sleep: Callable[[float], None] = time.sleep,
) -> object:
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    payload = _read(request, timeout=timeout, retries=retries, backoff=backoff, opener=opener, sleep=sleep)
    return _decode_json(payload, "GET", url)


def post_json(
    url: str,
    body: dict[str, object],
    *,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    backoff: float = DEFAULT_BACKOFF,
    opener: Opener = _default_opener,
    sleep: Callable[[float], None] = time.sleep,
) -> object:
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"User-Agent": USER_AGENT, "Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    payload = _read(request, timeout=timeout, retries=retries, backoff=backoff, opener=opener, sleep=sleep)
    return _decode_json(payload, "POST", url)


def post_form(
    url: str,
    fields: dict[str, str],
    *,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    backoff: float = DEFAULT_BACKOFF,
    opener: Opener = _default_opener,
    sleep: Callable[[float], None] = time.sleep,
) -> object:
    """POST ``application/x-www-form-urlencoded`` fields, expect JSON back.

    Used by the OSM Overpass client, whose API takes the query in a ``data``
    form field and returns JSON when the query requests ``[out:json]``.
    """
    data = urllib.parse.urlencode(fields).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "User-Agent": USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        method="POST",
    )
    payload = _read(request, timeout=timeout, retries=retries, backoff=backoff, opener=opener, sleep=sleep)
    return _decode_json(payload, "POST", url)


def cached_get_json(url: str, cache_path: Path, *, timeout: int = DEFAULT_TIMEOUT, refresh: bool = False) -> object:
    """Return cached JSON if present, otherwise fetch and cache it."""
    if cache_path.exists() and not refresh:
        return json.loads(cache_path.read_text(encoding="utf-8"))
    data = get_json(url, timeout=timeout)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return data
