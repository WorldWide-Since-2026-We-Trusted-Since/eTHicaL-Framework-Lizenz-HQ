# Implementation-Lizenz — Template (Child-Schicht)

Eine **Implementation-Lizenz** ist eine *anerkannte* SPDX-Lizenz (z. B.
`Apache-2.0`, `MIT`, `EUPL-1.2`), die für eine konkrete Komponente **unter** die
Headquarter-Lizenz gestellt wird. Sie regelt die technischen/urheberrechtlichen
Details; die Headquarter-Schicht regelt die unabdingbaren Axiome.

## So machst du eine Komponente UECF-konform

1. **Wähle** eine OSI-approved / FSF-libre Implementation-Lizenz und lege ihren
   Volltext unter `LICENSES/<SPDX-ID>.txt` ab (siehe REUSE-Spezifikation).

2. **Kennzeichne** jede Datei mit einem SPDX-Header (oder per `REUSE.toml`):

   <!-- REUSE-IgnoreStart -->
   ```text
   SPDX-FileCopyrightText: 2026 <Dein Name>
   SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND <SPDX-ID>
   ```
   <!-- REUSE-IgnoreEnd -->

3. **Erzeuge** ein Implementation-Manifest `implementation/<component>.json`
   nach dem Schema `tools/schema/implementation.schema.json` (Beispiel:
   [`example-implementation.json`](./example-implementation.json)).

4. **Validiere** lokal:

   ```bash
   python3 -m reuse lint
   python3 tools/uecf_validate.py implementation/<component>.json
   ```

5. **Registriere** (optional, on-chain) die Bindung über den Bridge-Registry-
   Vertrag (`contracts/BridgeLicenseRegistry.sol`). Damit wird die Beziehung
   zwischen Komponente, Implementation-Lizenz und Headquarter-Axiomen
   unveränderlich und öffentlich nachvollziehbar protokolliert.

## Pflichtfelder des Manifests (Kurzform)

| Feld | Bedeutung |
|------|-----------|
| `spdxExpression` | Muss `LicenseRef-UECF-Headquarter-1.0 AND <Impl>` enthalten |
| `implementationLicense` | Die gewählte SPDX-Lizenz |
| `sourceUrl` | Öffentlich abrufbarer Quellort (Axiom A1) |
| `declarations.prohibitedUse` | `false` = bestätigt: kein verbotener Einsatz (A2) |
| `declarations.nonDiscrimination` | `true` = bestätigt: Nicht-Diskriminierung (A3) |
| `declarations.dsaNoticeAndAction` | URL der Notice-and-Action-Stelle (A4) |
