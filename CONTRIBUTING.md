# Mitwirken

Danke für dein Interesse am UECF Proof of Best Practices Concept.

## Grundregeln

- **REUSE-Konformität:** Jede neue Datei braucht SPDX-Angaben — entweder als
  Inline-Header oder über [`REUSE.toml`](REUSE.toml). Prüfe mit:
  ```bash
  python3 -m reuse lint
  ```
- **Tests müssen grün sein:**
  ```bash
  python3 -m pytest -q   # Validator
  forge test             # Smart Contracts
  ```
- **Headquarter-Schicht ist immutabel:** Änderungen an den Axiomen A1–A4 oder am
  Headquarter-Lizenztext erfordern eine neue Major-Version
  (`LicenseRef-UECF-Headquarter-2.0`), keine In-place-Änderung von v1.0.

## Lizenzierung von Beiträgen

Mit einem Beitrag stimmst du zu, dass dein Code unter
`LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0` und Dokumentation unter
`LicenseRef-UECF-Headquarter-1.0 AND CC-BY-4.0` veröffentlicht wird.

## Commit-/PR-Hinweise

- Kleine, fokussierte Commits.
- Beschreibe das *Warum*, nicht nur das *Was*.
- Verlinke betroffene Axiome/Checks, wenn relevant.
