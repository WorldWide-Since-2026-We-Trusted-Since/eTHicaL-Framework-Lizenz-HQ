# Datenquellen & Lizenz-Analyse

Diese Analyse ordnet jede integrierte Quelle ihrer **eigenen** Lizenz zu und
zeigt, wie sie über das UECF an die Headquarter-Axiome gebunden wird. Maßgeblich
ist die Registry [`ingest/sources.py`](../ingest/sources.py); pro Quelle erzeugt
[`ingest/manifest.py`](../ingest/manifest.py) ein validierbares
Implementation-Manifest unter [`implementation/`](../implementation/).

> **Keine Rechtsberatung.** Lizenz-Zuordnungen sind nach bestem Wissen und vor
> Produktiveinsatz mit den jeweils aktuellen Bedingungen der Quelle zu prüfen.

## Übersicht

| Quelle | Art | Lizenz (SPDX) | UECF-Bindung | Status |
|--------|-----|---------------|--------------|--------|
| **PeeringDB** | Datensatz | `CC-BY-4.0` | `LicenseRef-UECF-Headquarter-1.0 AND CC-BY-4.0` | live abrufbar (REST) |
| **Packet Clearing House (IXP-Directory)** | Datensatz | `LicenseRef-PCH-Terms` | `… AND LicenseRef-PCH-Terms` | live abrufbar (JSON) |
| **CAIDA Resource Catalog** | Datensatz | `LicenseRef-CAIDA-AUP` | `… AND LicenseRef-CAIDA-AUP` | live abrufbar (GraphQL) |
| **GLEIF LEI-Index** | Datensatz | `CC0-1.0` | `… AND CC0-1.0` | live abrufbar (REST) |
| **OpenStreetMap (Overpass)** | Datensatz | `ODbL-1.0` | `… AND ODbL-1.0` | live abrufbar (Overpass) + Dump-Fallback |
| **Wikidata** | Datensatz | `CC0-1.0` | `… AND CC0-1.0` | live abrufbar (SPARQL) + Dump-Fallback |
| **SPDX License List Data** | Standard | `CC0-1.0` | `… AND CC0-1.0` | GitHub |
| **Package URL (purl)** | Standard | `MIT` | `… AND MIT` | GitHub |
| **OmniBOR** | Standard | `CC-BY-4.0` | `… AND CC-BY-4.0` | GitHub |

## Quellen im Detail

### PeeringDB — `CC-BY-4.0`
Globale Datenbank zu Netzen (ASNs), Internet-Exchanges (IX), Facilities und
Organisationen. Daten stehen unter **CC-BY-4.0** → Pflicht zur **Namensnennung**.
REST-API: `https://www.peeringdb.com/api` (anonym rate-limitiert; HTTP 429 bei
zu vielen Anfragen — die Pipeline degradiert dann sauber).
Relevanz „IBX": Facility-Datensätze enthalten die **Equinix IBX**-Standorte
(Organisation „Equinix, Inc."), abrufbar via `fac?name__contains=Equinix`.

### Packet Clearing House (PCH) — `LicenseRef-PCH-Terms`
Die im Auftrag als „Clearing House" bezeichnete Quelle. PCH betreibt
Route-Server an IXPs und veröffentlicht ein weltweites **IXP-Verzeichnis**
(`https://www.pch.net/api/ixp/directory`). Die vom Nutzer gelieferte IXP-Tabelle
ist eine Darstellung dieses Verzeichnisses (gleiche Größenordnung: ~1305
Einträge). PCH publiziert keine eindeutige Standard-SPDX-Lizenz → Platzhalter
`LicenseRef-PCH-Terms` mit Hinweis auf Klärungsbedarf und Namensnennung.

### CAIDA Resource Catalog — `LicenseRef-CAIDA-AUP`
Katalog aus Datasets, Papers, Recipes, Presentations (GraphQL-API:
`https://api.catalog.caida.org/v1/`). CAIDA-Daten unterliegen i. d. R. der
**CAIDA Acceptable Use Policy** (Zitier-/Acknowledgement-Pflichten,
Re-Identifikationsverbot) statt einer Standard-Open-Source-Lizenz →
`LicenseRef-CAIDA-AUP`.

### GLEIF — Legal Entity Identifier (LEI) — `CC0-1.0`
Die **Institutions-Schicht**: der LEI ist der universelle Schlüssel für Banken,
Zentralbanken, Staatsfonds und Unternehmen. GLEIF veröffentlicht den globalen
LEI-Index unter **CC0-1.0** (REST: `https://api.gleif.org/api/v1/lei-records`).
Die Pipeline löst beispielhaft Institutionen auf (EZB, Norges Bank, IBRD/Weltbank)
und bindet sie via `dataset-gleif.json` an die Headquarter-Axiome.

> Hinweis: CC0 betrifft die LEI-**Referenzdaten** von GLEIF selbst. Verknüpfte
> Drittdaten (z. B. kommerzielle Profile) haben eigene, abweichende Lizenzen.

### OpenStreetMap (Overpass API) — `ODbL-1.0`
Geodaten zur Internet-Infrastruktur (z. B. `telecom=data_center`) aus der
**Overpass-API** (`https://overpass-api.de/api/interpreter`). OSM-Daten stehen
unter der **Open Database License (ODbL-1.0)**: Namensnennung „© OpenStreetMap
contributors" und **Share-Alike** für abgeleitete Datenbanken; „Produced Works"
dürfen unter eigenen Bedingungen stehen, sofern Quelle und Lizenz genannt werden.
Der Client [`ingest/osm.py`](../ingest/osm.py) nutzt nur die Standardbibliothek,
**paginiert räumlich** über Bounding-Box-Kacheln (Overpass kennt kein Offset-
Paging) und behandelt **HTTP 429** (Overpass-Slot-Limit) über die zentrale
Retry-/Backoff-Schicht in [`ingest/http.py`](../ingest/http.py). Ist die API nicht
erreichbar/rate-limitiert, greift der **dokumentierte Dump-Fallback**
[`data/samples/osm-overpass-sample.json`](../data/samples/osm-overpass-sample.json).

### Wikidata (SPARQL) — `CC0-1.0`
Strukturierte Daten aus dem **Wikidata Query Service**
(`https://query.wikidata.org/sparql`). Wikidata-Aussagen sind unter **CC0-1.0**
gemeinfrei. Der Client [`ingest/wikidata.py`](../ingest/wikidata.py) ist
stdlib-only, **paginiert via SPARQL `LIMIT`/`OFFSET`** und behandelt **HTTP 429**
über dieselbe Retry-Schicht. Die Default-Abfrage selektiert Entitäten mit
GLEIF-**LEI** (Property `P1278`) und verbindet Wikidata damit direkt mit der
Institutions-Schicht (GLEIF). Dump-Fallback:
[`data/samples/wikidata-lei-sample.json`](../data/samples/wikidata-lei-sample.json).

> Hinweis: CC0 gilt für die **Aussagen/Daten** in Wikidata. Eingebundene Medien
> (z. B. Bilder aus Wikimedia Commons) können eigene Lizenzen haben.

### Finanz-/Behördendaten — analysiert, (noch) nicht live integriert
Aus dem Transkript genannte Quellen; hier mit ihrer Lizenz-/Zugriffslage. Sie
lassen sich nach demselben Muster (eigene Lizenz `AND` Headquarter) anbinden,
sind aber wegen API-Keys bzw. kommerzieller Bedingungen nicht im Live-Lauf:

| Quelle | Lizenz/Bedingungen | Warum nicht live | Schlüssel |
|--------|--------------------|------------------|-----------|
| **OpenCorporates** | Daten u. a. `CC-BY-SA-4.0`/ODbL, API-ToS | API-Key nötig, Share-Alike beachten | LEI/Company-Nr. |
| **SWFI** (Sovereign Wealth Fund Institute) | kommerziell | kostenpflichtig, keine Re-Distribution | Entity-ID |
| **ION Group** (Private-Equity-Daten) | kommerziell | kostenpflichtig | Entity-ID |
| **OECD** (Investment Policy / Stats) | OECD-Terms, teils `CC-BY-4.0` | uneinheitlich pro Datensatz | Land/Indikator |
| **GovData / Open-Data-Portale** | `dl-de/by-2.0`, `CC-BY-4.0`, Public Domain | je Datensatz unterschiedlich (CKAN) | Dataset-ID |

Korrektur zum Transkript: die dortigen Beispielskripte nutzen Platzhalter
(`api.finance-data-provider.example`, Fake-API-Key, der LEI `5493006V410O4E5X0S55`
existiert **nicht**). Dieses PoC verwendet stattdessen die **echte** GLEIF-API.

### Standards (Software-Supply-Chain)
- **SPDX License List Data** (`CC0-1.0`): liefert das kanonische
  SPDX-Identifier-Vokabular, das UECF durchgängig verwendet.
- **Package URL / purl** (`MIT`): einheitliche Identifikation von Upstream-Paketen.
- **OmniBOR** (`CC-BY-4.0`): Artifact Dependency Graph / Input-Manifeste für
  Build-Provenienz. Exakten Lizenztext im Upstream-Repo verifizieren.

## Wie die Integration funktioniert

```
            ┌────────────────────────────────────────────┐
            │   Headquarter-Axiome A1–A4 (unumstößlich)    │
            └───────────────────────┬────────────────────┘
                                    │  AND (SPDX-Ausdruck)
  PeeringDB(CC-BY-4.0)·PCH(Ref)·CAIDA(Ref)·GLEIF(CC0)·OSM(ODbL)·Wikidata(CC0)·SPDX(CC0)·purl(MIT)·OmniBOR(CC-BY)
                                    │
                       je ein Implementation-Manifest
                  (implementation/dataset-<key>.json, validiert)
```

Jede Quelle behält ihre **eigene** Lizenz; das UECF legt die ethischen Axiome
**daneben** (nicht statt). Der Validator
([`tools/uecf_validate.py`](../tools/uecf_validate.py)) prüft für jedes Manifest
Schema, SPDX-Ausdruck (Headquarter-Bindung + vorhandener Lizenztext in
`LICENSES/`) und die Axiome A1–A4.

## Reproduktion

```bash
# Deterministisch (ohne Netz): Tabelle parsen + Manifeste erzeugen
python3 -m ingest.pipeline --offline

# Mit Live-Abruf (PeeringDB/PCH/CAIDA), Ergebnis in data/analysis-summary.json
python3 -m ingest.pipeline

# Alle erzeugten Manifeste validieren
for m in implementation/dataset-*.json; do python3 tools/uecf_validate.py "$m"; done
```
