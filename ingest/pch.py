# SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
# SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
"""Packet Clearing House (PCH) IXP directory client — the 'Clearing House'.

PCH publishes a global directory of Internet Exchange Points. The user-provided
IXP table is a rendering of this directory.
"""
from __future__ import annotations

from pathlib import Path

from .http import cached_get_json

DIRECTORY_URL = "https://www.pch.net/api/ixp/directory"


def directory(cache_dir: Path, *, refresh: bool = False) -> list[dict[str, object]]:
    payload = cached_get_json(DIRECTORY_URL, cache_dir / "pch-ixp-directory.json", refresh=refresh)
    if not isinstance(payload, list):
        raise TypeError("PCH directory response is not a list")
    return [row for row in payload if isinstance(row, dict)]
