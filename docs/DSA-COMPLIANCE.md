# DSA-Mapping (Verordnung (EU) 2022/2065)

Axiom **A4** verankert die Konformität mit dem Digital Services Act (DSA). Diese
Tabelle ordnet die UECF-Mechanismen den einschlägigen DSA-Pflichten zu. Sie ist
eine technische Orientierung, **keine Rechtsberatung** und nicht abschließend.

| DSA-Pflicht (vereinfacht) | DSA-Bezug* | UECF-Mechanismus |
|---------------------------|------------|------------------|
| Notice-and-Action-Verfahren | Art. 16 | Pflichtfeld `declarations.dsaNoticeAndAction` (URL) im Manifest; Check `A4:dsa-notice-and-action`. |
| Kontaktstelle | Art. 11/12 | `dsa.pointOfContact` in `headquarter-license.json`. |
| Transparenz / Nachvollziehbarkeit | Erwägungsgründe, Art. 14 | Axiom A1 (öffentlicher Quellcode) + Bridge-Registry (öffentliches, unveränderliches Log). |
| Begründung von Maßnahmen | Art. 17 | `reportBreach(componentId, axiom)` protokolliert das betroffene Axiom on-chain. |
| Abhilfe / Wiederherstellung | Art. 16/20 (Geist) | 30-Tage-Heilungsfenster (`cure`) vor `finalizeTermination`. |

\* Artikelangaben dienen der Orientierung; die genaue Anwendbarkeit hängt von
Rolle (Vermittlungsdienst, Hosting, Plattform, VLOP) und Einzelfall ab.

## „DSA 40"

Im Ausgangsdokument war von „DSA 40 konform" die Rede. Der DSA (VO (EU)
2022/2065) ist die maßgebliche Verordnung; eine eigenständige Norm „DSA 40"
existiert nicht. Das UECF referenziert daher durchgängig die offizielle
Verordnung. Sollte „40" auf einen bestimmten Artikel/Erwägungsgrund zielen,
lässt sich die obige Tabelle entsprechend ergänzen.

## Automatisierung im Code-Lifecycle

Die Idee „Notice-and-Action in den Code-Lifecycle einbetten" wird hier so
umgesetzt:

1. **Registrierung** verlangt eine funktionierende Notice-and-Action-URL
   (Validator-Check `A4`).
2. **Meldung** eines Verstoßes erfolgt über `reportBreach` und ist öffentlich.
3. **Abhilfe** über `cure` innerhalb der Frist; andernfalls automatische
   Beendigung der Rechte (`finalizeTermination`).
