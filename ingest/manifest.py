# SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
# SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
"""Generate UECF Implementation Manifests from the data-source registry.

Each external source becomes a UECF Covered Work: its own SPDX license is bound
to the Headquarter axioms via ``LicenseRef-UECF-Headquarter-1.0 AND <license>``.
The emitted manifests validate against ``tools/schema/implementation.schema.json``
and the Headquarter axiom checks in ``tools/uecf_validate.py``.
"""
from __future__ import annotations

from .sources import DataSource

HEADQUARTER_SPDX_ID = "LicenseRef-UECF-Headquarter-1.0"


def build_manifest(source: DataSource, *, version: str = "1.0.0") -> dict[str, object]:
    """Return an implementation manifest dict for a data source."""
    return {
        "uecfVersion": "1.0",
        "component": f"dataset-{source.key}",
        "version": version,
        "spdxExpression": f"{HEADQUARTER_SPDX_ID} AND {source.spdx_license}",
        "implementationLicense": source.spdx_license,
        "sourceUrl": source.homepage,
        "declarations": {
            "prohibitedUse": False,
            "nonDiscrimination": True,
            "dsaNoticeAndAction": source.notice_and_action,
        },
    }


def manifest_filename(source: DataSource) -> str:
    return f"dataset-{source.key}.json"
