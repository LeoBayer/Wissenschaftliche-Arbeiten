== Datengrundlage und Aussagekraft
<datengrundlage-und-aussagekraft>
Der ERP-Export umfasst 48 Monatswerte von Oktober 2022 bis September
2026 für beide Modelle zusammen. Ich fasse sie zu Geschäftsjahren von
Oktober bis September zusammen. Daraus ergeben sich zunächst 3.732,
4.087, 4.459 und 4.653 Räder. Durch Wessels' Korrektur steigt der letzte
Wert auf 4.759. Ein korrigierter Export und ein Beleg zum Rahmenvertrag
liegen nicht vor. Auch bleibt offen, ob die erfassten Mengen durch
Lieferengpässe begrenzt waren.

Um die Verfahren zu vergleichen, prognostiziere ich zunächst mit den
ersten 24 Monaten die folgenden zwölf Monate. Danach wiederhole ich den
Test mit 36 Monaten. Die jeweils vorherzusagenden Werte gehen nicht in
die Schätzung ein. Für den Vergleich verwende ich die bereinigten
Ist-Werte; wann die Korrektur damals bekannt gewesen wäre, ist nicht
belegt.

#figure(
  align(center)[#table(
    columns: 4,
    align: (auto,right,right,right,),
    table.header([Verfahren], [Basis 2027], [Monats-MAE], [Monats-MSE],),
    table.hline(),
    [Saisonal-naiv], [4.759,00], [32,17], [1.451,17],
    [Jahrestrend mit Saisonanteilen], [5.122,50], [16,72], [470,09],
    [Saisonale Drift], [5.101,33], [18,79], [673,17],
    [Holt-Winters additiv], [5.203,83], [22,85], [854,54],
  )]
  , kind: table
  )

Der MAE misst den mittleren absoluten Monatsfehler in Rädern, der MSE
den mittleren quadratischen Fehler in Rädern². Beide beziehen sich auf
dieselben 24 Testmonate. Beim Jahrestrend beträgt die Abweichung der
Jahresmenge +17 bzw. −60,67 Räder (Ist minus Prognose).

Für den saisonalen Vergleich verwende ich zusätzlich additives
Holt-Winters mit zwölf Monaten Saisonlänge und festen Parametern α=0,2,
β=0,1 und γ=0,2. Das Anfangsniveau ist der Mittelwert der ersten zwölf
Monate, der Anfangstrend null; die Anfangssaison ergibt sich aus den
Abweichungen vom Mittelwert. Ab Monat 13 werden die Größen aktualisiert.
Die Parameter werden nicht auf den Testjahren optimiert.

#figure(
  align(center)[#table(
    columns: 2,
    align: (auto,right,),
    table.header([Annahmen zum Jahrestrend], [Prognose inkl. Zusatz],),
    table.hline(),
    [Originaldaten, kein Zusatz], [5.016,50],
    [Korrektur, kein Zusatz], [5.122,50],
    [Originaldaten, 180 zusätzlich], [5.196,50],
    [Korrektur, 180 zusätzlich], [5.302,50],
  )]
  , kind: table
  )

Die vier Rechnungen zeigen die Abhängigkeit von den beiden Annahmen,
nicht die Wahrscheinlichkeit einer bestimmten Nachfrage. Aus nur zwei
Jahrestests lässt sich kein belastbares 95-%-Prognoseintervall
bestimmen. Deshalb würde ich die Planung monatlich mit den neuen Mengen
abgleichen. Falls der Rahmenvertrag nicht zusätzlich ist, entfällt der
Aufschlag; dann liegt die bereinigte Basis bei rund 5.100 Rädern. Ein
möglicher Kapazitätspuffer ist davon getrennt zu entscheiden.

== Quellen und Transparenz
<quellen-und-transparenz>
Eigene Fallansicht und Gespräche mit Claudia Wessels und Frank Terhörst
vom 28.10.2026; ERP\_Export\_Nachfrage\_Okt2022-Sep2026.csv (48
Monatswerte).
