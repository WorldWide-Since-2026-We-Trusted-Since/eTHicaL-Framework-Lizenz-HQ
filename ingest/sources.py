# SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
# SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
"""Registry of external data sources and standards, with their licenses.

This module is the heart of the "integrate into my license" requirement: every
external source is mapped to its own recognised SPDX license (or a documented
``LicenseRef-*``). The UECF manifest generator then binds that license to the
Headquarter axioms via the expression
``LicenseRef-UECF-Headquarter-1.0 AND <license>``.

License assignments are best-effort and MUST be verified against each source's
current terms before production use. This is a proof of concept, not legal
advice.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Kind(str, Enum):
    DATASET = "dataset"
    STANDARD = "standard"


@dataclass(frozen=True)
class DataSource:
    """A data source or standard that is integrated into the UECF."""

    key: str
    name: str
    kind: Kind
    homepage: str
    #: SPDX identifier (or LicenseRef-*) under which the source's content is offered.
    spdx_license: str
    #: Where the license / terms are published.
    license_url: str
    #: Required attribution string when redistributing.
    attribution: str
    #: Public contact / abuse / notice endpoint (maps to DSA Axiom A4).
    notice_and_action: str
    #: Optional machine API base URL.
    api: str | None = None
    #: Related upstream GitHub repositories.
    github: tuple[str, ...] = field(default_factory=tuple)
    #: Free-text caveat about the license assignment.
    note: str = ""


SOURCES: tuple[DataSource, ...] = (
    DataSource(
        key="peeringdb",
        name="PeeringDB",
        kind=Kind.DATASET,
        homepage="https://www.peeringdb.com/",
        spdx_license="CC-BY-4.0",
        license_url="https://www.peeringdb.com/aup",
        attribution="Data from PeeringDB (https://www.peeringdb.com/), CC-BY-4.0.",
        notice_and_action="https://www.peeringdb.com/aup",
        api="https://www.peeringdb.com/api",
        github=(
            "https://github.com/peeringdb/peeringdb.git",
            "https://github.com/peeringdb/peeringdb-py.git",
            "https://github.com/peeringdb/docs.git",
        ),
        note="PeeringDB facility records include Equinix IBX sites (org 'Equinix, Inc.').",
    ),
    DataSource(
        key="pch",
        name="Packet Clearing House (IXP Directory)",
        kind=Kind.DATASET,
        homepage="https://www.pch.net/",
        spdx_license="LicenseRef-PCH-Terms",
        license_url="https://www.pch.net/about/terms",
        attribution="IXP directory data courtesy of Packet Clearing House (https://www.pch.net/).",
        notice_and_action="https://www.pch.net/about/contact",
        api="https://www.pch.net/api/ixp",
        github=(),
        note="The 'Clearing House' source. PCH does not publish a standard SPDX "
        "license for the directory; LicenseRef-PCH-Terms is a placeholder pending "
        "confirmation. The user-provided IXP table is a rendering of this directory.",
    ),
    DataSource(
        key="caida",
        name="CAIDA Resource Catalog",
        kind=Kind.DATASET,
        homepage="https://catalog.caida.org/",
        spdx_license="LicenseRef-CAIDA-AUP",
        license_url="https://www.caida.org/about/legal/aup/",
        attribution="Includes data from CAIDA (https://www.caida.org/), subject to the CAIDA AUP.",
        notice_and_action="https://www.caida.org/about/legal/aup/",
        api="https://api.catalog.caida.org/v1/",
        github=(),
        note="The catalog API is GraphQL. Most CAIDA datasets are governed by the "
        "CAIDA Acceptable Use Policy rather than a standard open license.",
    ),
    DataSource(
        key="gleif",
        name="GLEIF Legal Entity Identifier (LEI) index",
        kind=Kind.DATASET,
        homepage="https://www.gleif.org/",
        spdx_license="CC0-1.0",
        license_url="https://www.gleif.org/en/about/open-data/gleif-data-use-policy",
        attribution="LEI data from GLEIF (https://www.gleif.org/), published under CC0-1.0.",
        notice_and_action="https://www.gleif.org/en/about/contact",
        api="https://api.gleif.org/api/v1",
        github=("https://github.com/Gleif-LEI",),
        note="Universal entity key (LEI) for the institutional layer: banks, central "
        "banks, sovereign wealth funds and companies. GLEIF publishes the LEI data "
        "under CC0-1.0; downstream use of linked records still requires care.",
    ),
    DataSource(
        key="osm",
        name="OpenStreetMap (Overpass API)",
        kind=Kind.DATASET,
        homepage="https://www.openstreetmap.org/",
        spdx_license="ODbL-1.0",
        license_url="https://opendatacommons.org/licenses/odbl/1-0/",
        attribution="© OpenStreetMap contributors, data under ODbL-1.0.",
        notice_and_action="https://www.openstreetmap.org/fixthemap",
        api="https://overpass-api.de/api/interpreter",
        github=(
            "https://github.com/openstreetmap/openstreetmap-website.git",
            "https://github.com/drolbr/Overpass-API.git",
        ),
        note="Map data is licensed ODbL-1.0 (share-alike for derived databases; "
        "'Produced Works' may carry their own terms with attribution). The Overpass "
        "client paginates spatially over bounding-box tiles and handles HTTP 429.",
    ),
    DataSource(
        key="wikidata",
        name="Wikidata",
        kind=Kind.DATASET,
        homepage="https://www.wikidata.org/",
        spdx_license="CC0-1.0",
        license_url="https://www.wikidata.org/wiki/Wikidata:Licensing",
        attribution="Data from Wikidata (https://www.wikidata.org/), published under CC0-1.0.",
        notice_and_action="https://www.wikidata.org/wiki/Wikidata:Contact_the_development_team",
        api="https://query.wikidata.org/sparql",
        github=("https://github.com/wikimedia/wikidata-query-rdf.git",),
        note="Structured data is dedicated to the public domain under CC0-1.0. The "
        "SPARQL client paginates via LIMIT/OFFSET and handles HTTP 429; the default "
        "query links entities to their GLEIF LEI (property P1278).",
    ),
    DataSource(
        key="spdx-license-list",
        name="SPDX License List Data",
        kind=Kind.STANDARD,
        homepage="https://spdx.org/licenses/",
        spdx_license="CC0-1.0",
        license_url="https://github.com/spdx/license-list-data/blob/main/LICENSE.code",
        attribution="SPDX License List data is published under CC0-1.0.",
        notice_and_action="https://github.com/spdx/license-list-data/issues",
        api=None,
        github=(
            "https://github.com/spdx/license-list-data.git",
            "https://github.com/spdx/license-list-XML.git",
            "https://github.com/spdx/LicenseListPublisher.git",
        ),
        note="Provides the canonical SPDX identifier vocabulary used throughout UECF.",
    ),
    DataSource(
        key="purl",
        name="Package URL (purl) specification",
        kind=Kind.STANDARD,
        homepage="https://github.com/package-url/purl-spec",
        spdx_license="MIT",
        license_url="https://github.com/package-url/purl-spec/blob/master/LICENSE",
        attribution="Package URL specification, MIT licensed.",
        notice_and_action="https://github.com/package-url/purl-spec/issues",
        api=None,
        github=("https://github.com/package-url/purl-spec",),
        note="Used to identify upstream packages in supply-chain metadata.",
    ),
    DataSource(
        key="omnibor",
        name="OmniBOR specification",
        kind=Kind.STANDARD,
        homepage="https://omnibor.io/",
        spdx_license="CC-BY-4.0",
        license_url="https://github.com/omnibor/spec/blob/main/LICENSE",
        attribution="OmniBOR specification (https://omnibor.io/).",
        notice_and_action="https://github.com/omnibor/spec/issues",
        api=None,
        github=("https://github.com/omnibor/spec/",),
        note="Artifact dependency graph / input manifests for build provenance. "
        "Verify exact license text in the upstream repo before relying on it.",
    ),
)


def by_key(key: str) -> DataSource:
    for source in SOURCES:
        if source.key == key:
            return source
    raise KeyError(key)


def datasets() -> tuple[DataSource, ...]:
    return tuple(s for s in SOURCES if s.kind is Kind.DATASET)


def standards() -> tuple[DataSource, ...]:
    return tuple(s for s in SOURCES if s.kind is Kind.STANDARD)
