#import "tokens.typ": *
// Semantic components: labels remain meaningful without color.
#let study-box(kind: "note", title: "Hinweis", body) = {
  let accent = if kind == "assumption" { study-amber }
    else if kind == "limitation" { study-rose }
    else { study-accent }
  block(width: 100%, breakable: true, inset: 11pt,
    fill: accent.lighten(95%),
    stroke: (left: 2.5pt + accent), radius: (right: 4pt),
    above: 10pt, below: 10pt)[
    #text(size: 9pt, weight: "bold", fill: accent)[#upper(title)]
    #v(4pt)
    #body
  ]
}
#let study-metric(value: "", label: "", detail: "") = block(
  width: 100%, inset: 12pt, fill: study-soft,
  stroke: .5pt + study-line, radius: 5pt,
)[
  #text(size: 9pt, fill: study-muted)[#label]
  #v(3pt)
  #text(size: 22pt, weight: "bold", fill: study-accent-strong)[#value]
  #v(2pt)
  #text(size: 8.5pt, fill: study-muted)[#detail]
]
