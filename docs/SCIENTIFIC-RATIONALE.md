# Wissenschaftliche Einordnung

## 1. Problemstellung

Lizenz-Compliance in heterogenen Software-Ökosystemen verursacht hohe
**Transaktionskosten**: Jede Wiederverwendung erfordert eine Abklärung der
Kompatibilität, der Pflichten und (zunehmend) der regulatorischen Vorgaben
(z. B. Digital Services Act, AI Act). Klassische Ansätze adressieren entweder
nur die *technische* Ebene (SPDX/REUSE) oder nur die *ethische* Ebene
(Ethical-Source-Lizenzen), selten beides in einem prüfbaren Modell.

## 2. Beitrag des UECF

Das UECF konzipiert Lizenzierung als **mehrschichtiges, kryptographisch
verankerbares Governance-Protokoll**:

- **Ontologische Basisschicht (Headquarter):** axiomatische Verankerung
  ethischer Normen (Integrität, Friedenspflicht, Nicht-Diskriminierung,
  DSA-Konformität). Sie ist *immutable* und damit über das gesamte Ökosystem
  hinweg kohärent auslegbar.
- **Modulare Subsysteme (Implementation):** technische Spezifikationen unter
  Verwendung standardisierter Kennzeichnungsschemata (SPDX, REUSE).
- **Synchronisationsschicht (Bridge):** ein öffentliches, append-only Register,
  das Bindungen unveränderlich dokumentiert und damit den Konsens über den
  Lizenzstatus herstellt.

## 3. Theoretische Verortung

| Konzept | Bezug |
|---------|-------|
| **Transaktionskostentheorie** (Coase/Williamson) | Standardisierung + maschinelle Checks senken Such-, Verhandlungs- und Durchsetzungskosten. |
| **Mechanism Design** | Der Lebenszyklus (register→breach→cure→terminate) ist ein Anreizmechanismus zur Selbstdurchsetzung. |
| **Self-executing contracts** (Szabo) | Die Headquarter-Lizenz wird durch Smart Contracts zu einem selbstvollziehenden Rechtsinstrument. |
| **Hierarchische Normensysteme** (Kelsen, Stufenbau) | Headquarter als „Grundnorm", Implementation als nachgeordnete Norm. |
| **Ethical Source Licensing** | A1–A3 folgen dem Muster wertegebundener Lizenzen, aber additiv statt ersetzend. |

## 4. Eigenschaften und Grenzen

**Stärken**

- Kompatibel mit OSI/FSF, da die durchsetzbare Permissions-Ebene eine anerkannte
  Lizenz bleibt.
- Maschinell verifizierbar: JSON-Schemas + Validator liefern reproduzierbare,
  CI-fähige Prüfungen.
- Transparenz und Unveränderlichkeit durch die Bridge.

**Grenzen (ehrlich benannt)**

- Ethische Selbstauskünfte (A2/A3) sind *nicht* maschinell beweisbar; das Modell
  dokumentiert Zusagen, ersetzt aber keine Aufsicht/Audit.
- Die rechtliche Durchsetzbarkeit zusätzlicher Verpflichtungen variiert je
  Jurisdiktion und bedarf juristischer Prüfung.
- „Ethical Source"-Klauseln können von der OSI als nicht-Open-Source eingestuft
  werden; deshalb wirkt die Headquarter-Schicht *additiv* und lässt die
  Implementation-Lizenz unangetastet.

## 5. Schlussfolgerung

Durch die Trennung von unveränderlichem ethischem Kern, austauschbarer
technischer Lizenz und transparenter Registry entsteht ein dynamisches,
regulatorisch anschlussfähiges Lizenz-Ökosystem — ein belastbarer
*Proof of Best Practices Concept*, der als Grundlage für eine juristisch
begleitete Weiterentwicklung dienen kann.
