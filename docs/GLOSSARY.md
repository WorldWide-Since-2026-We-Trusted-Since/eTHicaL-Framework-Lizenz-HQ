# Glossar

| Begriff | Bedeutung |
|---------|-----------|
| **UECF** | Unified Ethical Compliance Framework — das hier vorgestellte dreischichtige Lizenzmodell. |
| **Headquarter-Lizenz** | Unumstößliche Wurzelschicht; verankert die Axiome A1–A4. SPDX: `LicenseRef-UECF-Headquarter-1.0`. |
| **Implementation-Lizenz** | Anerkannte SPDX-Lizenz (z. B. Apache-2.0, MIT, EUPL-1.2), die unter die Headquarter-Schicht gestellt wird. |
| **Bridge** | Synchronisations-/Registry-Schicht; dokumentiert Bindungen unveränderlich und steuert den Lizenz-Lebenszyklus. |
| **Covered Work** | Ein Werk, das den SPDX-Ausdruck `LicenseRef-UECF-Headquarter-1.0 AND <Impl>` führt. |
| **Axiom (A1–A4)** | Nicht-derogierbare Grundpflicht: A1 Informationsfreiheit, A2 Friedenspflicht, A3 Ethik-Matrix, A4 DSA-Konformität. |
| **SPDX** | Software Package Data Exchange — Standard für maschinenlesbare Lizenzangaben. |
| **REUSE** | FSFE-Spezifikation für vollständige, maschinenlesbare Urheber-/Lizenzangaben je Datei. |
| **Manifest** | JSON-Datei, die eine Komponente als Covered Work deklariert (Schema: `tools/schema/implementation.schema.json`). |
| **Cure Window** | 30-Tage-Frist zur Heilung eines gemeldeten Axiom-Verstoßes (Headquarter-Lizenz §5.2). |
| **Arbiter** | On-chain-Rolle, die Verstöße melden darf (im PoC eine Adresse; produktiv besser Multisig/DAO). |
| **DSA** | Digital Services Act, Verordnung (EU) 2022/2065. |
