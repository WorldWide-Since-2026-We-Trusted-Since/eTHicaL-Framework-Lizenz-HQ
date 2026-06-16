# SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
# SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
"""Tests for the UECF compliance validator."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import uecf_validate as v


@pytest.fixture()
def valid_manifest(repo_root: Path) -> dict[str, object]:
    path = repo_root / "implementation" / "example-implementation.json"
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _write(tmp_path: Path, manifest: dict[str, object]) -> Path:
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def test_example_manifest_is_compliant(repo_root: Path) -> None:
    manifest = repo_root / "implementation" / "example-implementation.json"
    report = v.validate(manifest, repo_root)
    assert report.ok, report.render()
    assert {r.check_id for r in report.results} >= {
        "manifest-schema",
        "headquarter-schema",
        "spdx-expression",
        "A1:source-public",
        "A2:no-prohibited-use-declaration",
        "A3:non-discrimination-declaration",
        "A4:dsa-notice-and-action",
    }


def test_headquarter_license_matches_schema(repo_root: Path) -> None:
    hq = v.load_json(repo_root / "headquarter" / "headquarter-license.json")
    schema = v.load_json(repo_root / "tools" / "schema" / "headquarter.schema.json")
    result = v._schema_check("headquarter-schema", hq, schema)
    assert result.ok, result.message


def test_a2_prohibited_use_true_fails(
    repo_root: Path, tmp_path: Path, valid_manifest: dict[str, object]
) -> None:
    manifest = copy.deepcopy(valid_manifest)
    manifest["declarations"]["prohibitedUse"] = True  # type: ignore[index]
    report = v.validate(_write(tmp_path, manifest), repo_root)
    assert not report.ok
    failed = [r.check_id for r in report.results if not r.ok]
    assert "A2:no-prohibited-use-declaration" in failed


def test_a3_discrimination_fails(
    repo_root: Path, tmp_path: Path, valid_manifest: dict[str, object]
) -> None:
    manifest = copy.deepcopy(valid_manifest)
    manifest["declarations"]["nonDiscrimination"] = False  # type: ignore[index]
    report = v.validate(_write(tmp_path, manifest), repo_root)
    assert not report.ok
    assert any(r.check_id == "A3:non-discrimination-declaration" and not r.ok for r in report.results)


def test_a4_missing_notice_and_action_fails(
    repo_root: Path, tmp_path: Path, valid_manifest: dict[str, object]
) -> None:
    manifest = copy.deepcopy(valid_manifest)
    manifest["declarations"]["dsaNoticeAndAction"] = "not-a-url"  # type: ignore[index]
    report = v.validate(_write(tmp_path, manifest), repo_root)
    assert not report.ok


def test_spdx_expression_without_headquarter_fails(
    repo_root: Path, tmp_path: Path, valid_manifest: dict[str, object]
) -> None:
    manifest = copy.deepcopy(valid_manifest)
    manifest["spdxExpression"] = "Apache-2.0"
    report = v.validate(_write(tmp_path, manifest), repo_root)
    assert not report.ok
    assert any(r.check_id == "spdx-expression" and not r.ok for r in report.results)


def test_unknown_implementation_license_fails(
    repo_root: Path, tmp_path: Path, valid_manifest: dict[str, object]
) -> None:
    manifest = copy.deepcopy(valid_manifest)
    manifest["implementationLicense"] = "NOT-A-REAL-LICENSE-9000"
    manifest["spdxExpression"] = "LicenseRef-UECF-Headquarter-1.0 AND NOT-A-REAL-LICENSE-9000"
    report = v.validate(_write(tmp_path, manifest), repo_root)
    assert not report.ok
    assert any(r.check_id == "spdx-expression" and not r.ok for r in report.results)


def test_main_returns_zero_for_valid(repo_root: Path) -> None:
    manifest = repo_root / "implementation" / "example-implementation.json"
    assert v.main([str(manifest)]) == 0


def test_main_returns_two_for_missing_file(tmp_path: Path) -> None:
    assert v.main([str(tmp_path / "does-not-exist.json")]) == 2
