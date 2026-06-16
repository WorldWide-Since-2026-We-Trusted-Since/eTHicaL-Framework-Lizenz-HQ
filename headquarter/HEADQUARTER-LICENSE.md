# Headquarter-Lizenz — Erläuterung (Axiomatische Schicht)

> Dies ist die **erläuternde** Begleitdokumentation. Der **verbindliche** Lizenztext
> ist [`LICENSES/LicenseRef-UECF-Headquarter-1.0.txt`](../LICENSES/LicenseRef-UECF-Headquarter-1.0.txt).
> Die maschinenlesbare Form ist [`headquarter-license.json`](./headquarter-license.json).
>
> **Keine Rechtsberatung.** Dieses Repository ist ein *Proof of Concept*. Vor einem
> produktiven Einsatz ist qualifizierter juristischer Rat einzuholen.

## Rolle im Framework

Die Headquarter-Lizenz ist die **Root Trust Authority** des UECF. Sie ist
**unumstößlich** (`immutable: true`) und wird **neben** (nicht statt) einer
anerkannten SPDX-Lizenz angewandt. Ein konformes Werk trägt daher immer einen
**SPDX-Ausdruck** der Form:

```
LicenseRef-UECF-Headquarter-1.0 AND <Implementation-License>
```

Beispiel: `LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0`.

So bleibt das Werk **OSI-/FSF-kompatibel** (über die Implementation-Lizenz),
erbt aber zwingend die ethischen Pflichten der Headquarter-Schicht.

## Die vier Axiome

| ID | Titel | Kerninhalt | Automatischer Check |
|----|-------|-----------|---------------------|
| A1 | Informationsfreiheit | Quellcode + SPDX/REUSE-Metadaten öffentlich abrufbar | `source-public` |
| A2 | Friedenspflicht | Kein Einsatz für Waffen/Schaden | `no-prohibited-use-declaration` |
| A3 | Ethik-Matrix | Würde, Nächstenliebe, Hoffnung; keine Diskriminierung | `non-discrimination-declaration` |
| A4 | DSA-Konformität | Notice-and-Action + Kontaktstelle (VO (EU) 2022/2065) | `dsa-notice-and-action` |

Jedes Axiom ist mit einem **maschinellen Check** verknüpft, den der Validator
(`tools/uecf_validate.py`) und der Bridge-Registry-Vertrag teilweise erzwingen
können. Maschinelle Checks ersetzen keine rechtliche Prüfung, senken aber die
Transaktionskosten der Lizenzabklärung erheblich.

## Warum „neben" und nicht „statt"?

Eine eigene, vollständig neue Lizenz, die bestehende Verträge ersetzt, ist
rechtlich kaum durchsetzbar und inkompatibel mit dem Open-Source-Ökosystem.
Der UECF-Ansatz folgt stattdessen dem Muster etablierter **Ethical-Source**- und
**Dual-Layer**-Lizenzen: eine schmale, klar umrissene Zusatzschicht (Axiome A1–A4)
über einer bewährten, breit akzeptierten Lizenz. Das ist die „Best Practice",
die Kompatibilität, Rechtssicherheit und ethische Bindung verbindet.
