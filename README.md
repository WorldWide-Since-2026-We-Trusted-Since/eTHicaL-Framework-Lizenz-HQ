# UECF — Unified Ethical Compliance Framework

**Proof of Best Practices Concept** für ein dreischichtiges, standardkonformes
Lizenzmodell: eine **Headquarter-Lizenz** als unumstößliches ethisches Fundament,
darunter eine **Bridge**-Synchronisationsschicht und beliebig viele
**Implementation-Lizenzen** (anerkannte SPDX-Lizenzen) für konkrete Komponenten.

> **Keine Rechtsberatung.** Dieses Repository ist ein technischer Machbarkeitsnachweis
> (Proof of Concept). Für den produktiven Einsatz ist qualifizierter juristischer
> Rat einzuholen. Bereitstellung „AS IS", ohne Gewähr.

[![REUSE status](https://img.shields.io/badge/REUSE-compliant-brightgreen)](https://reuse.software/)

---

## Idee in einem Satz

Statt eine neue Lizenz zu erfinden, die bestehende Verträge *ersetzt* (rechtlich
kaum durchsetzbar), legt das UECF eine schmale, **unabänderliche ethische Schicht
NEBEN** eine bewährte Open-Source-Lizenz — ausgedrückt als SPDX-Ausdruck:

```
LicenseRef-UECF-Headquarter-1.0 AND <Implementation-License>
```

Das ist kompatibel mit dem gesamten SPDX/REUSE-Ökosystem, OSI-/FSF-tauglich und
zugleich an die vier Axiome A1–A4 gebunden.

## Die drei Schichten

| Schicht | Rolle | Protokoll | Fokus | Artefakt |
|---------|-------|-----------|-------|----------|
| **Headquarter** | Axiomatische Basis (Root Trust Authority) | Smart Contract | Ethik, Frieden, DSA | [`HeadquarterLicense.sol`](contracts/HeadquarterLicense.sol), [`LICENSES/LicenseRef-UECF-Headquarter-1.0.txt`](LICENSES/LicenseRef-UECF-Headquarter-1.0.txt) |
| **Bridge** | Synchronisations-/Registry-Layer | On-chain Registry | Konsens, Integrität, Lifecycle | [`BridgeLicenseRegistry.sol`](contracts/BridgeLicenseRegistry.sol) |
| **Implementation** | Konkrete Anwendung | SPDX / REUSE | Code, Effizienz, Portabilität | [`ImplementationLicense.sol`](contracts/ImplementationLicense.sol), [Template](implementation/IMPLEMENTATION-LICENSE-TEMPLATE.md) |

Die vier Axiome (A1 Informationsfreiheit, A2 Friedenspflicht, A3 Ethik-Matrix,
A4 DSA-Konformität) sind in [`headquarter/headquarter-license.json`](headquarter/headquarter-license.json)
maschinenlesbar hinterlegt und je mit einem automatischen Check verknüpft.

## Was macht das zu „Best Practices"?

- **SPDX + REUSE**: Jede Datei hat Urheber- und Lizenzangaben; `reuse lint` ist Teil der CI.
- **Layering statt Ersetzung**: Ethische Schicht *additiv* zu einer anerkannten Lizenz (Muster etablierter Ethical-Source-Lizenzen).
- **Maschinell prüfbar**: JSON-Schemas + Validator (`tools/uecf_validate.py`) automatisieren die Lizenz­abklärung.
- **Smart Contracts nach Stand der Technik**: custom errors, `immutable` Anker, keine Upgrade-Hintertür, vollständige Foundry-Tests. Die Bridge enthält einen **Kill-Switch** `revokeCompliance(lei)` (LEI-basiertes `isRevoked`-Mapping, `onlyValid`-Modifier, Events) — Compliance lässt sich pro Rechtsträger sperren/wiederherstellen.
- **DSA-Bezug**: Notice-and-Action und Kontaktstelle sind Pflichtfelder (VO (EU) 2022/2065).
- **CI/CD**: GitHub Actions prüft REUSE, Python-Tests und Solidity-Tests bei jedem Push.

## Schnellstart

```bash
# 1. Python-Werkzeuge
python3 -m pip install -r requirements.txt charset-normalizer

# 2. SPDX/REUSE-Konformität prüfen
python3 -m reuse lint

# 3. Beispiel-Manifest gegen die Axiome validieren
python3 tools/uecf_validate.py implementation/example-implementation.json

# 4. Python-Tests
python3 -m pytest -q

# 5. Smart-Contract-Tests (Foundry)
forge test
```

Oder kompakt über den Makefile-Wrapper:

```bash
make install   # Abhängigkeiten
make test      # reuse + python + validator + forge
```

## Datenintegration (IXP / PeeringDB / PCH / CAIDA / GLEIF)

Der `ingest/`-Layer verbindet reale Internet-Infrastruktur- **und Institutions-**
Datenquellen mit deiner Lizenz: jede Quelle behält ihre **eigene** Lizenz und
wird über einen SPDX-Ausdruck an die Headquarter-Axiome gebunden.

| Quelle | Lizenz (SPDX) | Zugriff |
|--------|---------------|---------|
| **PeeringDB** (IX, Facilities inkl. **Equinix IBX**) | `CC-BY-4.0` | REST live |
| **Packet Clearing House** (IXP-Directory, „Clearing House") | `LicenseRef-PCH-Terms` | JSON live |
| **CAIDA Resource Catalog** | `LicenseRef-CAIDA-AUP` | GraphQL live |
| **GLEIF** (LEI-Index: Banken, Zentralbanken, Staatsfonds) | `CC0-1.0` | REST live |
| **OpenStreetMap** (Overpass: Infrastruktur-Geodaten) | `ODbL-1.0` | Overpass live + Dump-Fallback |
| **Wikidata** (SPARQL: Entitäten mit LEI/P1278) | `CC0-1.0` | SPARQL live + Dump-Fallback |
| **SPDX / purl / OmniBOR** (Standards) | `CC0-1.0` / `MIT` / `CC-BY-4.0` | GitHub |

Der **LEI (Legal Entity Identifier)** ist der universelle Schlüssel der
Institutions-Schicht. Alle Ingest-Clients nutzen **nur die Python-
Standardbibliothek**, paginieren (Skip/Offset bzw. räumliche Kacheln) und
behandeln **Rate-Limits (HTTP 429)** zentral in [`ingest/http.py`](ingest/http.py)
(Retry mit `Retry-After`-Backoff); ist eine Quelle nicht erreichbar, greift ein
dokumentierter **Dump-Fallback** unter [`data/samples/`](data/samples/).
Finanz-/Behördenquellen mit API-Key oder kommerziellen Bedingungen
(OpenCorporates, SWFI, ION, OECD, GovData) sind in
[`docs/DATA-LICENSES.md`](docs/DATA-LICENSES.md) lizenzrechtlich analysiert.

```bash
python3 -m ingest.pipeline --offline   # deterministisch: Tabelle parsen + Manifeste bauen
python3 -m ingest.pipeline             # + Live-Abruf -> data/analysis-summary.json
make validate-all                      # alle erzeugten Manifeste validieren
```

Für jede Quelle entsteht ein validiertes Manifest unter
[`implementation/dataset-*.json`](implementation/). Details + Lizenz-Analyse:
[`docs/DATA-LICENSES.md`](docs/DATA-LICENSES.md).

## Repository-Struktur

```
.
├── LICENSES/                       # Volltexte aller Lizenzen (REUSE)
│   └── LicenseRef-UECF-Headquarter-1.0.txt   # verbindlicher Headquarter-Text
├── headquarter/                    # Axiomatische Schicht
│   ├── HEADQUARTER-LICENSE.md      #   Erläuterung
│   └── headquarter-license.json    #   maschinenlesbar (A1–A4 + DSA)
├── implementation/                 # Child-Schicht
│   ├── IMPLEMENTATION-LICENSE-TEMPLATE.md
│   ├── example-implementation.json # Beispiel-Manifest (Covered Work)
│   └── dataset-*.json              # generierte Manifeste je Datenquelle
├── ingest/                         # Datenintegration (PeeringDB/PCH/CAIDA/GLEIF + Lizenz-Registry)
├── data/                           # raw/ (gelieferte IXP-Tabelle) + analysis-summary.json
├── contracts/                      # Solidity (Headquarter/Implementation/Bridge)
├── test/                           # Foundry-Tests
├── tools/                          # Validator + JSON-Schemas
├── tests/                          # Python-Tests (Validator + Ingestion)
├── examples/sample-project/        # Beispiel einer Covered-Work-Quelldatei
├── docs/                           # Architektur, Wissenschaft, DSA-Mapping, Daten-Lizenzen
└── .github/workflows/ci.yml        # CI
```

## Weiterführende Dokumentation

- [Architektur](docs/ARCHITECTURE.md) — die drei Schichten im Detail
- [Wissenschaftliche Einordnung](docs/SCIENTIFIC-RATIONALE.md)
- [DSA-Mapping](docs/DSA-COMPLIANCE.md) — Bezug zur VO (EU) 2022/2065
- [Datenquellen & Lizenz-Analyse](docs/DATA-LICENSES.md)
- [Glossar](docs/GLOSSARY.md)
- [Mitwirken](CONTRIBUTING.md)

## Lizenz

Dieses Projekt ist selbst UECF-konform: Quellcode unter
`LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0`, Dokumentation unter
`LicenseRef-UECF-Headquarter-1.0 AND CC-BY-4.0`, triviale Daten/Konfiguration
unter `CC0-1.0`. Details siehe SPDX-Header bzw. [`REUSE.toml`](REUSE.toml).
