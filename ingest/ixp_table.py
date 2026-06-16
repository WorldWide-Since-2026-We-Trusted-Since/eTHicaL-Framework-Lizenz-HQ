# SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
# SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
"""Parser for the user-provided IXP table (a rendering of the PCH directory).

The table is tab-separated with 11 columns. The ``Region`` column uses a
"group header" layout: it is only populated on the first row of each region
block and empty on continuation rows, so we forward-fill it.

Traffic values use SI suffixes (K/M/G/T). ``parse_si`` converts them to floats
(bits per second) for analysis.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, asdict
from pathlib import Path

COLUMNS = [
    "region",
    "country",
    "city",
    "name",
    "participants",
    "peak",
    "average",
    "ipv6",
    "prefixes",
    "founded",
    "url",
]

_SI = {"K": 1e3, "M": 1e6, "G": 1e9, "T": 1e12, "P": 1e15}
_REGION_COUNT = re.compile(r"\s*\(\d+\)\s*$")


@dataclass(frozen=True)
class IxpRecord:
    region: str
    country: str
    city: str
    name: str
    participants: int | None
    peak_bps: float | None
    average_bps: float | None
    ipv6: str
    prefixes: int | None
    founded: str
    url: str


def parse_si(value: str) -> float | None:
    """Convert an SI-suffixed string like '9.8T' or '920M' to a float."""
    value = (value or "").strip()
    if not value:
        return None
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([KMGTP]?)", value, re.IGNORECASE)
    if not match:
        return None
    number = float(match.group(1))
    suffix = match.group(2).upper()
    return number * _SI.get(suffix, 1.0)


def _int(value: str) -> int | None:
    value = (value or "").strip().replace(",", "")
    return int(value) if value.isdigit() else None


def _clean_region(value: str) -> str:
    return _REGION_COUNT.sub("", value).strip()


def parse(path: Path) -> list[IxpRecord]:
    """Parse the IXP TSV into records, forward-filling the region column."""
    records: list[IxpRecord] = []
    current_region = ""
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        rows = list(reader)
    for index, row in enumerate(rows):
        if index == 0:
            continue  # header
        if not any(cell.strip() for cell in row):
            continue
        # Pad/truncate to the expected width.
        cells = (row + [""] * len(COLUMNS))[: len(COLUMNS)]
        region = _clean_region(cells[0])
        if region:
            current_region = region
        records.append(
            IxpRecord(
                region=current_region,
                country=cells[1].strip(),
                city=cells[2].strip(),
                name=cells[3].strip(),
                participants=_int(cells[4]),
                peak_bps=parse_si(cells[5]),
                average_bps=parse_si(cells[6]),
                ipv6=cells[7].strip(),
                prefixes=_int(cells[8]),
                founded=cells[9].strip(),
                url=cells[10].strip(),
            )
        )
    return records


def to_dicts(records: list[IxpRecord]) -> list[dict[str, object]]:
    return [asdict(record) for record in records]
