# Architektur des UECF

Das UECF ist ein **mehrschichtiges Governance-Framework** für Lizenzen. Es trennt
*unabänderliche ethische Normen* (Headquarter) von *austauschbaren technischen
Lizenzbedingungen* (Implementation) und verbindet beide über eine *transparente
Registry* (Bridge).

```
            ┌─────────────────────────────────────────────┐
            │            HEADQUARTER (Root)                │
            │  Axiome A1–A4 · unumstößlich · immutable      │
            │  LicenseRef-UECF-Headquarter-1.0              │
            └───────────────────────┬─────────────────────┘
                                    │  vererbt (AND)
            ┌───────────────────────┴─────────────────────┐
            │               BRIDGE (Sync)                  │
            │  Registry: bindet Komponente ↔ SPDX ↔ Axiome │
            │  Lifecycle: register · breach · cure · term. │
            └───────────────────────┬─────────────────────┘
                                    │  referenziert
       ┌────────────────┬───────────┴───────────┬────────────────┐
       │ Implementation │   Implementation       │ Implementation │
       │   Apache-2.0   │       MIT              │    EUPL-1.2    │
       └────────────────┴───────────────────────┴────────────────┘
```

## 1. Headquarter — die axiomatische Schicht

- **Verbindlicher Text:** `LICENSES/LicenseRef-UECF-Headquarter-1.0.txt`
- **Maschinenlesbar:** `headquarter/headquarter-license.json` (validiert gegen
  `tools/schema/headquarter.schema.json`)
- **On-chain:** `contracts/HeadquarterLicense.sol`

Die Schicht definiert vier nicht-derogierbare Axiome und stellt einen
Compliance-Gate-Modifier (`onlyCompatible`) bereit, den jede Implementation-
Klasse erbt. Der Vertrag ist bewusst **ohne Owner und ohne Upgrade-Pfad** —
das ist die technische Entsprechung von „unumstößlich".

## 2. Bridge — die Synchronisationsschicht

- **On-chain:** `contracts/BridgeLicenseRegistry.sol`

Die Bridge ist das öffentliche, unveränderliche Protokoll, das jede Bindung
„Komponente ↔ SPDX-Ausdruck ↔ Headquarter-Axiome" festhält. Sie implementiert
den Lebenszyklus aus Abschnitt 5 der Headquarter-Lizenz:

1. `register(componentId, spdxExpression, sourceUrl)` — nur zulässig, wenn der
   Ausdruck die Headquarter-LicenseRef enthält.
2. `reportBreach(componentId, axiom)` — nur durch den `arbiter`; eröffnet das
   30-Tage-Heilungsfenster (`CURE_WINDOW`).
3. `cure(componentId)` — Registrant heilt innerhalb der Frist.
4. `finalizeTermination(componentId)` — permissionless nach Fristablauf.

## 3. Implementation — die Child-Schicht

- **On-chain:** `contracts/ImplementationLicense.sol` (erbt von Headquarter)
- **Off-chain:** Manifest nach `tools/schema/implementation.schema.json`

<!-- REUSE-IgnoreStart -->
Eine konkrete Komponente wählt eine anerkannte SPDX-Lizenz, kennzeichnet ihre
Dateien (`SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND <Impl>`)
und hinterlegt ein Manifest. Der Validator prüft Schema + Axiome + SPDX-Ausdruck.
<!-- REUSE-IgnoreEnd -->

## Vererbung als Kernmechanik

On-chain ist die Vererbung wörtlich (`ImplementationLicense is HeadquarterLicense`).
Off-chain entspricht ihr der SPDX-`AND`-Operator: Beide Lizenzbedingungen gelten
kumulativ. Eine Weitergabe ohne die Headquarter-Bindung ist per Abschnitt 4 der
Lizenz untersagt und wird von Validator und Registry zurückgewiesen.

## Vertrauensgrenzen / Threat model (PoC)

| Annahme | Bemerkung |
|---------|-----------|
| `arbiter` ist vertrauenswürdig | Im PoC eine einzelne Adresse; produktiv besser ein Multisig/DAO. |
| Off-chain-Erklärungen sind wahr | `prohibitedUse`/`nonDiscrimination` sind Selbstauskünfte; maschinelle Checks können sie nicht beweisen, nur dokumentieren. |
| `block.timestamp` | Für ein 30-Tage-Fenster ist die Validator-Manipulation (Sekunden) irrelevant. |
| Quell-URL erreichbar | A1 prüft Format; eine Erreichbarkeitsprüfung kann ergänzt werden. |
