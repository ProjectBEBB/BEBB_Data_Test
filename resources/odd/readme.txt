README: Dateien für TEI Roma und Validierung

Dieses Verzeichnis enthält die folgenden wichtigen Dateien für die Arbeit mit TEI Roma und die Validierung von TEI-Dokumenten:

1. ODD-Datei
Dateiname: BEBB_schema.odd
Zweck:
Anpassung des TEI-Schemas in TEI Roma.
Ermöglicht das Hinzufügen, Entfernen oder Modifizieren von Elementen und Attributen.
Kann in verschiedene Validierungsformate exportiert werden (z. B. .rng, .xsd).
Wie verwenden?:
- Datei in TEI Roma öffnen.
- Schema anpassen.
- Schema exportieren (z. B. .rng oder .xsd), um Dokumente zu validieren.

2. RNG-Datei
Dateiname: BEBB_schema.rng
Zweck:
Validierung von TEI-Dokumenten gegen das angepasste Schema.
Kann in XML-Editoren oder Validierungstools verwendet werden.

Zusammenfassung des Workflows
Anpassung der Datei BEBB_schema.odd in TEI Roma.
Generierung eines Validierungsschemas durch exportieren als BEBB_schema.rng.
Validierung von Dokumenten durch Verlinkung mit BEBB_schema.rng.