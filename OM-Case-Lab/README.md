# OM · Entscheidungsatelier

Eigene Quarto-Lernanalyse zum unbewerteten Ersatzakku-Fall. Keine offizielle Lehrstuhllösung, keine Uni-Backendintegration, keine Originalunterlagen und keine vollständigen Persona-Gespräche in diesem Repository.

## Bauen und prüfen

Im Projektordner `quarto render` ausführen. Das Ergebnis entsteht in `_site/`.

`/home/leo/.openclaw/workspace/.venv/bin/python check_site.py` prüft Modell, Browserinteraktionen, lokale Links, Exporte, fünf Bildschirmbreiten und Hell/Dunkel. Es erzeugt die verlinkte zweiseitige Probe-PDF mit Chromium; keine LaTeX-Installation nötig. Sämtliche Testserver werden anschließend beendet. Screenshots und Prüfberichte bleiben im privaten lokalen Review-Verzeichnis außerhalb dieses Repositories.

Das geprüfte `_site/` wird ausschließlich nach `docs/OM-Case-Lab/` kopiert. Andere Websitebereiche bleiben unverändert. `downloads/ersatzakku-probeabgabe.pdf` ist die Abgabeergänzung, keine bereits eingereichte Lösung.

## Rechen- und Datenstand

`model.js` enthält die pure Modelllogik; `lab.js` das lokale UI, `data.json` die aggregierten Ausgangswerte. Der Nachfragefaktor ist ein Szenario, keine Wahrscheinlichkeit. Die zusammengeführte Mengenreihe ist wegen Bestell-/Fakturaabgrenzung vorläufig. Die Fixkostenauskunft der Persona wurde im Gespräch korrigiert und ist kein unabhängiger Vertragsbeleg. Details stehen auf der Methodenseite.

Die Website hält keine Nutzerkonten, speichert Eingaben nicht automatisch und schickt Parameter nicht an KI-/Uni-Dienste. Alle Fälle, spätere Bonusabgaben und Versionsänderungen sind getrennt zu prüfen; dieses Paket behandelt nur den Übungsfall vom 23.10.2026.
