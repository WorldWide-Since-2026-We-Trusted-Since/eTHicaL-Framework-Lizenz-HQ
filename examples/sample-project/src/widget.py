# SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
# SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
"""Minimal example of a UECF Covered Work source file.

Note the SPDX-License-Identifier above: it binds the Headquarter axioms
(LicenseRef-UECF-Headquarter-1.0) to a recognised implementation license
(Apache-2.0). Any redistribution must keep this expression (inheritance, A1).
"""
from __future__ import annotations


def greet(name: str) -> str:
    """A deliberately trivial function — the point is the licensing header."""
    return f"Hello, {name}. This component is UECF-covered."
