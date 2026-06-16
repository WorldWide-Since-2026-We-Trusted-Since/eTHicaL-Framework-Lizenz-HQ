# SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
# SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
"""End-to-end UECF data-integration pipeline.

Steps:
  1. Parse the provided IXP table (PCH directory rendering).
  2. Optionally fetch live data (PeeringDB, PCH, CAIDA); degrade gracefully when
     offline or rate-limited.
  3. Emit a UECF Implementation Manifest per data source/standard.
  4. Write a machine-readable analysis summary.

Run: ``python3 -m ingest.pipeline`` (add ``--offline`` to skip network calls).
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from . import caida, gleif, osm, pch, peeringdb, wikidata
from .http import HttpError
from .ixp_table import IxpRecord, parse, to_dicts
from .manifest import build_manifest, manifest_filename
from .sources import SOURCES

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TABLE = REPO_ROOT / "data" / "raw" / "pch-ixp-directory.tsv"
CACHE_DIR = REPO_ROOT / "data" / "cache"
SAMPLES_DIR = REPO_ROOT / "data" / "samples"
IMPL_DIR = REPO_ROOT / "implementation"
SUMMARY_PATH = REPO_ROOT / "data" / "analysis-summary.json"
OSM_SAMPLE = SAMPLES_DIR / "osm-overpass-sample.json"
WIKIDATA_SAMPLE = SAMPLES_DIR / "wikidata-lei-sample.json"
OSM_TAG = "telecom=data_center"

# Representative institutions for the institutional layer (banks / central banks).
GLEIF_SAMPLE_QUERIES = (
    "European Central Bank",
    "Norges Bank",
    "International Bank for Reconstruction and Development",
)


def analyse_ixp_table(records: list[IxpRecord]) -> dict[str, object]:
    with_participants = [r for r in records if r.participants is not None]
    top = sorted(with_participants, key=lambda r: r.participants or 0, reverse=True)[:10]
    return {
        "total_ixps": len(records),
        "countries": len({r.country for r in records if r.country}),
        "by_region": dict(Counter(r.region for r in records if r.region).most_common()),
        "with_ipv6_figure": sum(1 for r in records if r.ipv6),
        "with_participants": len(with_participants),
        "top_by_participants": [
            {"name": r.name, "country": r.country, "participants": r.participants} for r in top
        ],
    }


def fetch_peeringdb(offline: bool, refresh: bool) -> dict[str, object]:
    if offline:
        return {"status": "skipped (offline)"}
    try:
        exchanges = peeringdb.exchanges(CACHE_DIR, refresh=refresh)
        equinix = peeringdb.equinix_ibx(CACHE_DIR, refresh=refresh)
    except HttpError as exc:
        return {"status": f"unreachable: {exc}"}
    countries = Counter(str(ix.get("country")) for ix in exchanges if ix.get("country"))
    return {
        "status": "ok",
        "license": "CC-BY-4.0",
        "total_exchanges": len(exchanges),
        "exchanges_with_ipv6": sum(1 for ix in exchanges if ix.get("proto_ipv6")),
        "top_countries": dict(countries.most_common(10)),
        "equinix_ibx_facilities": len(equinix),
    }


def fetch_pch(offline: bool, refresh: bool) -> dict[str, object]:
    if offline:
        return {"status": "skipped (offline)"}
    try:
        directory = pch.directory(CACHE_DIR, refresh=refresh)
    except HttpError as exc:
        return {"status": f"unreachable: {exc}"}
    return {
        "status": "ok",
        "total_entries": len(directory),
        "pch_hosted_route_servers": sum(1 for row in directory if str(row.get("pch")).lower() == "yes"),
    }


def fetch_caida(offline: bool, *, query: str = "ixp") -> dict[str, object]:
    if offline:
        return {"status": "skipped (offline)"}
    try:
        result = caida.search(query, first=5)
    except HttpError as exc:
        return {"status": f"unreachable: {exc}"}
    total = 0
    sample: list[str] = []
    if isinstance(result, dict):
        data = result.get("data")
        if isinstance(data, dict):
            search = data.get("search")
            if isinstance(search, dict):
                total = int(search.get("totalCount") or 0)
                edges = search.get("edges")
                if isinstance(edges, list):
                    for edge in edges:
                        if isinstance(edge, dict):
                            node = edge.get("node")
                            if isinstance(node, dict) and isinstance(node.get("name"), str):
                                sample.append(node["name"])
    return {"status": "ok", "query": query, "total_matches": total, "sample": sample}


def fetch_gleif(offline: bool, refresh: bool) -> dict[str, object]:
    if offline:
        return {"status": "skipped (offline)"}
    entities: list[dict[str, object]] = []
    try:
        for name in GLEIF_SAMPLE_QUERIES:
            _total, records = gleif.search_by_name(name, CACHE_DIR, size=1, refresh=refresh)
            if records:
                entities.append(gleif.summarise(records[0]))
    except HttpError as exc:
        return {"status": f"unreachable: {exc}"}
    if entities:
        SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
        sample = {
            "_source": "GLEIF /api/v1/lei-records",
            "_license": "CC0-1.0",
            "_key": "LEI (Legal Entity Identifier)",
            "_note": "Sample institutional entities resolved via the GLEIF LEI index.",
            "entities": entities,
        }
        (SAMPLES_DIR / "gleif-lei-sample.json").write_text(
            json.dumps(sample, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    return {"status": "ok", "license": "CC0-1.0", "key": "LEI", "sampled_entities": entities}


def _load_sample(path: Path) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def fetch_osm(offline: bool) -> dict[str, object]:
    if offline:
        return {"status": "skipped (offline)"}
    try:
        nodes = osm.paginate_tiles(OSM_TAG)
    except HttpError as exc:
        sample = _load_sample(OSM_SAMPLE)
        if sample is not None:
            summary = osm.summarise(osm.elements(sample))
            return {"status": f"dump-fallback ({exc})", "license": "ODbL-1.0", "tag": OSM_TAG, **summary}
        return {"status": f"unreachable: {exc}"}
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    OSM_SAMPLE.write_text(
        json.dumps(
            {
                "version": 0.6,
                "generator": "Overpass API",
                "_uecf_note": "Live slice (tag "
                + OSM_TAG
                + "). \u00a9 OpenStreetMap contributors, ODbL-1.0.",
                "elements": nodes[:25],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return {"status": "ok", "license": "ODbL-1.0", "tag": OSM_TAG, **osm.summarise(nodes)}


def fetch_wikidata(offline: bool) -> dict[str, object]:
    if offline:
        return {"status": "skipped (offline)"}
    try:
        rows = wikidata.entities_with_lei(page_size=200, max_pages=1)
    except HttpError as exc:
        sample = _load_sample(WIKIDATA_SAMPLE)
        if sample is not None:
            entities = wikidata.summarise(wikidata.bindings(sample))
            return {"status": f"dump-fallback ({exc})", "license": "CC0-1.0", "key": "LEI", "sampled_entities": entities[:5]}
        return {"status": f"unreachable: {exc}"}
    entities = wikidata.summarise(rows)
    return {"status": "ok", "license": "CC0-1.0", "key": "LEI (P1278)", "entities_with_lei": len(entities), "sample": entities[:5]}


def write_manifests() -> list[str]:
    IMPL_DIR.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for source in SOURCES:
        manifest = build_manifest(source)
        path = IMPL_DIR / manifest_filename(source)
        path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(str(path.relative_to(REPO_ROOT)))
    return written


def run(table_path: Path, *, offline: bool, refresh: bool) -> dict[str, object]:
    records = parse(table_path)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / "ixp-table.json").write_text(
        json.dumps(to_dicts(records), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    summary: dict[str, object] = {
        "ixp_table": analyse_ixp_table(records),
        "peeringdb": fetch_peeringdb(offline, refresh),
        "pch_live": fetch_pch(offline, refresh),
        "caida": fetch_caida(offline),
        "gleif": fetch_gleif(offline, refresh),
        "osm": fetch_osm(offline),
        "wikidata": fetch_wikidata(offline),
        "manifests": write_manifests(),
        "license_bindings": [
            {
                "source": s.name,
                "kind": s.kind.value,
                "spdxExpression": f"LicenseRef-UECF-Headquarter-1.0 AND {s.spdx_license}",
            }
            for s in SOURCES
        ],
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ingest.pipeline", description="UECF data-integration pipeline.")
    parser.add_argument("--table", type=Path, default=DEFAULT_TABLE, help="path to the IXP TSV table")
    parser.add_argument("--offline", action="store_true", help="skip all network calls")
    parser.add_argument("--refresh", action="store_true", help="bypass the on-disk cache")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run(args.table, offline=args.offline, refresh=args.refresh)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
