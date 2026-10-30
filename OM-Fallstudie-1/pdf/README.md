# Typst-Abgabefassung

Die maßgebliche PDF wird nativ mit Typst gesetzt. Designbausteine aus der vorhandenen Study-PDF-Vorlage, mit roten OM-Farben. Keine Browserdruck-Konvertierung.

Aus diesem Ordner:

```bash
/home/leo/.local/bin/quarto typst compile abgabe.typ ../downloads/MuensterRad-Fallstudie-1-Abgabe.pdf
```

`abgabe.typ`: Titel, roter Website-Link, Fußnote und native Mathematik. `empfehlung.txt`: 100-Wörter-Empfehlung. `daten-und-vergleich.typ`: Daten, Modellvergleich, Annahmen und Quellen. `theme/`: lokale, angepasste Layoutbausteine. Nach Änderungen zwei Seiten, Formelbild, Tabellen und PDF-Links prüfen; veröffentlichte und im Vault eingebettete PDF gemeinsam aktualisieren.
