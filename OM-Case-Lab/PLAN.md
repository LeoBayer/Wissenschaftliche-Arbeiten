# OM-Case-Lab — Umsetzungsstand

Auftrag von Leo am 23.10.2026: unbewerteten Ersatzakku-Fall bearbeiten, Quarto-Website mit veränderbaren Parametern erstellen und im eigenständig verständlichen PDF als Ergänzung verlinken. Keine Uni-Abgabe im aktuellen Auftrag. Keine Originalunterlagen oder vollständigen Persona-Gespräche veröffentlichen.

## Umfang dieses Pakets

- [x] Gezieltes Persona-Interview im angemeldeten Übungsfall begonnen, CSVs privat gesichert.
- [x] Mengen aus 23/54 Datensätzen aggregiert und ERP-Rechnungsbeträge geprüft.
- [x] Falsche anfängliche Auskunft zur Vermeidbarkeit von Fixkosten hinterfragt und Korrektur dokumentiert.
- [x] Bestell-/Absatzbruch identifiziert; keine durchgängig gesicherte Absatzreihe behauptet.
- [x] Rechenmodell mit konstantem, linearem und exponentiellem Ansatz, einheitlichem Mini-Rücktest, Entscheidungs- und Szenariorechnung implementiert.
- [x] Quarto-Seiten mit Originaldaten-/Annahmen-Trennung, Selbsttests und kompakter Probeempfehlung erstellt.
- [x] Rechenmodell und Interaktionen unabhängig prüfen; schmale/breite Ansicht und Hell/Dunkel ansehen.
- [x] PDF erstellen und Link/Seitenlayout prüfen.
- [x] Gezielt eigene Quellen/Builddateien committen und Website veröffentlichen; Live-Nachweis.

## Grenzen und nächster fachlicher Schritt

Die Kostenwerte stammen überwiegend aus einer KI-Persona, nicht einem Vertragsbeleg. Bestell-/Liefer-/Fakturaabgleich und tatsächliches Austauschpotenzial bleiben offen. Interviewvolltexte und Originaldateien liegen nur unter /home/leo/.local/state/openclaw/om-lernwerkstatt-2026-10-23/interview/. Die Website ist eine eigene Lernanalyse, kein öffentliches Archiv der Uni-Anwendung.

Nächster gemeinsamer Schritt: Leo erklärt Kostenrelevanz und Entscheidungsschwelle; anschließend Transferfall. Vor bewerteten Fällen jeweils tatsächlichen Auftrag, aktuelle Frist, erlaubtes Format und Datenlage prüfen. Keine späteren Bonusfälle in diesem Paket vorwegnehmen.

## Abnahme und Veröffentlichung

Implementierungscommit de76f91 auf origin main. Build/Modell-/Grenzfall-/Export-/Link-/Browserprüfungen erfolgreich; fünf Breiten 320–1440 px ohne Seitenüberlauf, Hell/Dunkel geprüft. PDF zwei Seiten,98-Wörter-Empfehlung und überprüfter anklickbarer Laborlink. Alle elf Live-Hauptdateien HTTP200 und SHA256-identisch zum geprüften Build. Vollprüfung und Screenshots privat außerhalb des Repositorys. Generierte Quarto-/Vendor-Dateien enthalten unveränderte upstream Whitespace-Stellen; eigene Quellen bestehen git diff --check. Keine Uni-Abgabe/kein Datei-Upload, keine produktiven Dienste geändert.

Livecheck-Nachtrag: Rundungsabweichung bei −1177,499999…EUR in der Ganz-Euro-Anzeige gefunden, Beträge vor Anzeige auf Cent normalisiert und gezielten UI-Regressionscheck ergänzt. Lokale Gesamtprüfung erneut erfolgreich; korrigierte Veröffentlichung folgt.

## UI-Überarbeitung 23.10.2026
Study-Lab-nahe Flächen und Karten mit roten OM-Akzenten; PDF-Button dauerhaft kontrastreich; überarbeitete Zahlenfelder ohne native Spinner; Parameter und Simulation ab 900 px nebeneinander, mobil gestapelt. Browserprüfung 320–1440 px, Hell/Dunkel, Modell/Exporte/Links erfolgreich.
