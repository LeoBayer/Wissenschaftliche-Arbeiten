#set page(paper: "a4", margin: 22mm)
#set text(font: "Liberation Sans", size: 11pt, lang: "de")
#set par(leading: .7em)
= MünsterRad · Prozessdesign
Mathematisches Begleitblatt zur Erklärwebsite · 10.11.2026

== Rückkopplung und Kapazität
Bei unabhängiger Fehlerwahrscheinlichkeit $p$ je Prüfbesuch werden Elektrik und Endkontrolle im Mittel $v = 1 / (1-p)$ Mal durchlaufen:
$ v = 1 + p + p^2 + dots = 1 / (1-p). $
Mit $T = 450$ produktiven Minuten pro Tag, $m$ parallelen Plätzen und $t$ Minuten je Besuch gilt ohne Nacharbeit $C = T m / t$, mit Nacharbeit hingegen
$ C = (T m (1-p)) / t. $
Heute beträgt die Elektrikkapazität $C_(E,0) = (450 dot 0.78) / 14 approx 25.07$ fertige Räder pro Tag. Mit Adapter gilt $C_(E,1) = (450 dot 0.97) / 15 = 29.10$. Die Endkontrolle schafft dann $C_(P,1) = (450 dot 3 dot 0.97) / 37 approx 35.39$.

Antrieb und Räder/Bremsen bleiben bei jeweils $900 / 31 approx 29.03$ Rädern pro Tag. Damit wechselt der Engpass. Bei Tagesfreigabe $r$ ist der langfristige Durchsatz $D = min(r, C_("Linie"))$: heute rund 25,07, danach 26,00 Räder pro Tag.

== Zielgrenze und Entscheidung
$ (450 (1-p)) / 15 >= 26 quad <=> quad p <= 1 - (26 dot 15) / 450 approx 13.33 percent. $
Der Prüfadapter kostet einmalig 8.500 €. Die erwarteten 3 % Fehlerquote sind noch keine eigene Betriebsmessung. Ein vierter Prüfstand beseitigt den heutigen Elektrikengpass nicht. Ohne Nutzungsdauer, laufende Kosten und Diskontsatz ist dies kein vollständiger Kapitalwertvergleich.

== Besuchsrate und Wartezeit
Bei $r=26$, $p=0.03$, $T=450$ und drei Prüfständen folgt
$ lambda = r / ((1-p)T) = 26 / (0.97 dot 450) approx 0.05956 $
Prüfbesuche pro Minute, also 26,80 pro Tag und 3,57 pro Stunde. Der mittlere Ankunftsabstand beträgt $1 / lambda approx 16.79$ Minuten. Bei mittlerer Prüfzeit $E[S]=37$ Minuten gilt
$ rho = (lambda E[S]) / 3 = (26 dot 37) / (0.97 dot 450 dot 3) approx 73.46 percent. $
Die Referenzsimulation liefert $W_q approx 19.5$ Minuten je Besuch, ohne Bearbeitungszeit. Über alle Besuche eines Rades ergibt sich näherungsweise $W_q / (1-p) approx 20.1$ Minuten reine Prüfwartezeit.

== Annahmen und Grenzen
M/G/3 mit gemeinsamer FIFO-Schlange und Poisson-Ankünften; diese Ankünfte wurden nicht gemessen. Prüfzeiten werden unabhängig aus 120 Messwerten gezogen (Mittel 37,00, Stichprobenstandardabweichung 27,03 Minuten). Rückläufer sind nur in der Gesamtrate enthalten. 20 Läufe mit je 20.000 Einschwing- und 200.000 ausgewerteten Besuchen. 95-%-Monte-Carlo-Intervall: 19,3–19,6 Minuten; nur Simulationsrauschen, keine Daten- oder Modellunsicherheit. Stationäres Langfristmodell, keine tägliche Leerung.

Quelle: eigene Aufbereitung der Fallbelege vom 09.11.2026. KI-unterstützte Lernanalyse, keine offizielle Musterlösung. Originaldateien und Gesprächsvolltexte bleiben privat. Dieses Begleitblatt ersetzt oder verändert nicht die eingereichte PDF.
