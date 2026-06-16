# SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
# SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
"""Offline, deterministic tests for the ingestion + license-binding layer."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import uecf_validate
from ingest import gleif, sources
from ingest.ixp_table import parse, parse_si
from ingest.manifest import build_manifest, manifest_filename

TABLE = Path(__file__).resolve().parent.parent / "data" / "raw" / "pch-ixp-directory.tsv"


@pytest.mark.parametrize(
    "raw,expected",
    [("920M", 920e6), ("2.19G", 2.19e9), ("9.8T", 9.8e12), ("647038", 647038.0), ("", None), ("n/a", None)],
)
def test_parse_si(raw: str, expected: float | None) -> None:
    assert parse_si(raw) == expected


def test_ixp_table_parses_and_forward_fills_region() -> None:
    records = parse(TABLE)
    assert len(records) > 1000
    # Every record must have a region carried over from its group header.
    assert all(record.region for record in records)
    # Known entry from the table.
    afg = [r for r in records if r.country == "Afghanistan"]
    assert afg and afg[0].participants == 20


def test_region_names_are_clean() -> None:
    records = parse(TABLE)
    regions = {r.region for r in records}
    # The "(123)" counts must be stripped.
    assert "Europe" in regions
    assert not any("(" in region for region in regions)


def test_every_source_binds_headquarter_and_has_license_text() -> None:
    root = uecf_validate.repo_root(TABLE.parent)
    available = uecf_validate.available_license_ids(root)
    for source in sources.SOURCES:
        assert source.spdx_license in available, f"missing LICENSES/{source.spdx_license}.txt"


def test_generated_manifests_are_compliant(tmp_path: Path) -> None:
    root = uecf_validate.repo_root(TABLE.parent)
    for source in sources.SOURCES:
        manifest = build_manifest(source)
        path = tmp_path / manifest_filename(source)
        path.write_text(json.dumps(manifest), encoding="utf-8")
        report = uecf_validate.validate(path, root)
        assert report.ok, report.render()


def test_gleif_summarise_extracts_institutional_fields() -> None:
    raw = {
        "type": "lei-records",
        "id": "549300DTUYXVMJXZNY75",
        "attributes": {
            "entity": {
                "legalName": {"name": "European Central Bank"},
                "jurisdiction": "DE",
                "category": "GENERAL",
                "status": "ACTIVE",
                "legalAddress": {"country": "DE", "city": "Frankfurt am Main"},
            }
        },
    }
    summary = gleif.summarise(raw)
    assert summary["lei"] == "549300DTUYXVMJXZNY75"
    assert summary["legalName"] == "European Central Bank"
    assert summary["country"] == "DE"
    # Missing/garbage input must degrade to None, never raise.
    empty = gleif.summarise({"id": 123})
    assert empty["lei"] is None and empty["legalName"] is None


def test_datasets_and_standards_partition() -> None:
    assert set(sources.datasets()) | set(sources.standards()) == set(sources.SOURCES)
    assert not (set(sources.datasets()) & set(sources.standards()))
