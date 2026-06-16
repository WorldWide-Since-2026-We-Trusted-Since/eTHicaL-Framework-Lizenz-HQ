#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
# SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
"""UECF compliance validator.

Validates a UECF Implementation Manifest against:

  1. the JSON schema for implementation manifests,
  2. the machine-readable Headquarter License (axioms A1-A4),
  3. the SPDX expression rules (Headquarter LicenseRef AND a recognised
     implementation license whose full text is present in ``LICENSES/``).

The validator is intentionally conservative: a machine check can only ever
*disprove* compliance or report "declared". It never asserts legal compliance.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import jsonschema

HEADQUARTER_SPDX_ID = "LicenseRef-UECF-Headquarter-1.0"


class Severity(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


@dataclass(frozen=True)
class CheckResult:
    """Outcome of a single named check."""

    check_id: str
    severity: Severity
    message: str

    @property
    def ok(self) -> bool:
        return self.severity is Severity.PASS


@dataclass(frozen=True)
class Report:
    manifest_path: Path
    results: list[CheckResult]

    @property
    def ok(self) -> bool:
        return all(result.ok for result in self.results)

    def render(self) -> str:
        lines = [f"UECF validation report for: {self.manifest_path}"]
        for result in self.results:
            mark = "ok  " if result.ok else "FAIL"
            lines.append(f"  [{mark}] {result.check_id}: {result.message}")
        verdict = "COMPLIANT (machine checks passed)" if self.ok else "NON-COMPLIANT"
        lines.append(f"=> {verdict}")
        return "\n".join(lines)


def repo_root(start: Path) -> Path:
    """Return the project root by walking up until ``LICENSES/`` is found."""
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "LICENSES").is_dir() and (candidate / "headquarter").is_dir():
            return candidate
    # Fall back to two levels up from this file (tools/ -> repo root).
    return Path(__file__).resolve().parent.parent


def load_json(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object at the top level")
    return data


def _schema_check(
    check_id: str, instance: dict[str, object], schema: dict[str, object]
) -> CheckResult:
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda error: error.path)
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.path) or "<root>"
        return CheckResult(
            check_id,
            Severity.FAIL,
            f"schema violation at '{location}': {first.message}",
        )
    return CheckResult(check_id, Severity.PASS, "schema valid")


def _str_field(manifest: dict[str, object], key: str) -> str:
    value = manifest.get(key)
    return value if isinstance(value, str) else ""


def _declarations(manifest: dict[str, object]) -> dict[str, object]:
    value = manifest.get("declarations")
    return value if isinstance(value, dict) else {}


def check_spdx_expression(
    manifest: dict[str, object], available_licenses: set[str]
) -> CheckResult:
    """SPDX expression must bind the Headquarter layer AND a present license."""
    expression = _str_field(manifest, "spdxExpression")
    implementation = _str_field(manifest, "implementationLicense")
    if HEADQUARTER_SPDX_ID not in expression:
        return CheckResult(
            "spdx-expression",
            Severity.FAIL,
            f"expression must contain '{HEADQUARTER_SPDX_ID}'",
        )
    if implementation and implementation not in expression:
        return CheckResult(
            "spdx-expression",
            Severity.FAIL,
            f"implementation license '{implementation}' missing from expression",
        )
    if implementation and implementation not in available_licenses:
        return CheckResult(
            "spdx-expression",
            Severity.FAIL,
            f"license text 'LICENSES/{implementation}.txt' is missing (REUSE)",
        )
    return CheckResult(
        "spdx-expression",
        Severity.PASS,
        f"binds Headquarter AND {implementation or '<implementation>'}",
    )


def check_axiom_a1(manifest: dict[str, object]) -> CheckResult:
    source = _str_field(manifest, "sourceUrl")
    if source.startswith(("http://", "https://")):
        return CheckResult("A1:source-public", Severity.PASS, f"public source: {source}")
    return CheckResult(
        "A1:source-public", Severity.FAIL, "sourceUrl must be a public http(s) URL"
    )


def check_axiom_a2(manifest: dict[str, object]) -> CheckResult:
    prohibited = _declarations(manifest).get("prohibitedUse")
    if prohibited is False:
        return CheckResult(
            "A2:no-prohibited-use-declaration",
            Severity.PASS,
            "declares no prohibited (weapons/harm) use",
        )
    return CheckResult(
        "A2:no-prohibited-use-declaration",
        Severity.FAIL,
        "declarations.prohibitedUse must be false",
    )


def check_axiom_a3(manifest: dict[str, object]) -> CheckResult:
    non_discrimination = _declarations(manifest).get("nonDiscrimination")
    if non_discrimination is True:
        return CheckResult(
            "A3:non-discrimination-declaration",
            Severity.PASS,
            "declares non-discrimination",
        )
    return CheckResult(
        "A3:non-discrimination-declaration",
        Severity.FAIL,
        "declarations.nonDiscrimination must be true",
    )


def check_axiom_a4(manifest: dict[str, object]) -> CheckResult:
    endpoint = _declarations(manifest).get("dsaNoticeAndAction")
    if isinstance(endpoint, str) and endpoint.startswith(("http://", "https://")):
        return CheckResult(
            "A4:dsa-notice-and-action",
            Severity.PASS,
            f"notice-and-action endpoint: {endpoint}",
        )
    return CheckResult(
        "A4:dsa-notice-and-action",
        Severity.FAIL,
        "declarations.dsaNoticeAndAction must be a public http(s) URL",
    )


def available_license_ids(root: Path) -> set[str]:
    licenses_dir = root / "LICENSES"
    if not licenses_dir.is_dir():
        return set()
    return {path.stem for path in licenses_dir.glob("*.txt")}


def validate(manifest_path: Path, root: Path) -> Report:
    schema_dir = root / "tools" / "schema"
    manifest = load_json(manifest_path)
    impl_schema = load_json(schema_dir / "implementation.schema.json")
    hq_schema = load_json(schema_dir / "headquarter.schema.json")
    hq_license = load_json(root / "headquarter" / "headquarter-license.json")
    licenses = available_license_ids(root)

    results = [
        _schema_check("manifest-schema", manifest, impl_schema),
        _schema_check("headquarter-schema", hq_license, hq_schema),
        check_spdx_expression(manifest, licenses),
        check_axiom_a1(manifest),
        check_axiom_a2(manifest),
        check_axiom_a3(manifest),
        check_axiom_a4(manifest),
    ]
    return Report(manifest_path=manifest_path, results=results)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="uecf_validate",
        description="Validate a UECF Implementation Manifest against the Headquarter axioms.",
    )
    parser.add_argument("manifest", type=Path, help="path to an implementation manifest JSON file")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="project root (defaults to autodetected repository root)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest_path: Path = args.manifest
    if not manifest_path.is_file():
        print(f"error: manifest not found: {manifest_path}", file=sys.stderr)
        return 2
    root: Path = args.root if args.root is not None else repo_root(manifest_path.parent)
    report = validate(manifest_path, root)
    print(report.render())
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
