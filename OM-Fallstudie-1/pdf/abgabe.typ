#import "theme/tokens.typ": *
#let study-accent = rgb("#a52c40")
#let study-accent-strong = rgb("#8b2332")
#import "theme/layout.typ": *
#import "theme/components.typ": *
#set document(title: "MünsterRad – Fallstudie 1: Nachfrageprognose", author: "Leo Bayer")
#set page(paper: "a4", margin: (top: 23mm, bottom: 22mm, x: 20mm))
#set text(font: "Libertinus Serif", size: 11.5pt, lang: "de")
#show: body => study-document(course: "Operations Management", kind: "Fallstudie 1", status: "Leo Bayer · 30. Oktober 2026", body)
#set par(leading: .48em, spacing: .6em)
#set heading(numbering: none)
#show heading.where(level: 1): set text(size: 14pt)
#show heading.where(level: 2): set text(size: 12pt)
#set table(inset: (x: 6pt, y: 4pt))
#set math.equation(numbering: none)

#text(size: 22pt, weight: "bold", fill: study-accent-strong)[MünsterRad – Nachfrageprognose]
#v(3pt)
#text(size: 10pt, fill: study-muted)[Fallstudie 1 · Leo Bayer · 30. Oktober 2026]
#v(7pt)
#block(width: 100%, inset: (x: 9pt, y: 7pt), fill: study-accent.lighten(95%), stroke: (left: 2pt + study-accent))[
  #text(fill: study-accent-strong, weight: "bold")[#link("https://leobayer.github.io/Wissenschaftliche-Arbeiten/OM-Fallstudie-1/")[Ergänzende Website: Rechenweg, Diagramme und Szenarien]]#footnote[Die Website ist eine freiwillige Ergänzung zur Falllösung. Die PDF enthält den vollständigen Rechenweg und ist ohne Website verständlich. Adresse: #link("https://leobayer.github.io/Wissenschaftliche-Arbeiten/OM-Fallstudie-1/")[leobayer.github.io/Wissenschaftliche-Arbeiten/OM-Fallstudie-1/].]
]

= Empfehlung
*Planzahl für das kommende Geschäftsjahr: 5.300 Räder.*

#read("empfehlung.txt")

= Rechenweg
Die bereinigten Jahresmengen sind 3.732, 4.087, 4.459 und 4.759 Räder. Für die Geschäftsjahre 2023 bis 2026 verwende ich den Zeitindex $t_i = i$ mit $i = 0, 1, 2, 3$. Daraus ergeben sich die Mittelwerte
$ overline(t) = (0 + 1 + 2 + 3) / 4 = "1,5", quad overline(q) = (3 thin 732 + 4 thin 087 + 4 thin 459 + 4 thin 759) / 4 = "4.259,25". $

Den linearen Trend $hat(q)(t) = a + b t$ schätze ich nach der Methode der kleinsten Quadrate:
$ b &= (sum_(i=0)^3 (t_i - overline(t))(q_i - overline(q))) / (sum_(i=0)^3 (t_i - overline(t))^2) = ("1.726,5") / 5 = "345,30", \
  a &= overline(q) - b overline(t) = "4.259,25" - "345,30" dot "1,5" = "3.741,30". $
Die Steigung beträgt damit 345,30 Räder pro Jahr. Für das Planjahr 2027 gilt $t=4$:
$ hat(q)(4) = "3.741,30" + "345,30" dot 4 = "5.122,50". $
Unter der Annahme, dass die 180 Räder zusätzlich anfallen, ergibt sich
$ q_("Plan") = hat(q)(4) + 180 = "5.302,50" approx 5 thin 300 " Räder". $
Für die Budgetplanung runde ich auf volle Hunderter. Die Abweichung beträgt nur 2,5 Räder. Einen zusätzlichen Sicherheitspuffer rechne ich nicht ein, da die Kosten einer Über- oder Unterplanung nicht bekannt sind.

#pagebreak()
#include "daten-und-vergleich.typ"
