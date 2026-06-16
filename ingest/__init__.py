# SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
# SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
"""UECF ingestion layer.

Connects external Internet-infrastructure datasets (PeeringDB, Packet Clearing
House, CAIDA) and software-supply-chain standards (SPDX, PURL, OmniBOR) to the
UECF licensing framework, mapping each source to its own SPDX license and
emitting UECF Implementation Manifests that bind those licenses to the
Headquarter axioms.
"""
