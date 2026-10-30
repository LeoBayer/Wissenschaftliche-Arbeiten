#import "tokens.typ": *
#let study-document(course: "Study Lab", kind: "Lernunterlage", status: "Arbeitsstand", body) = {
  set text(fill: study-ink, lang: "de")
  set par(justify: false, leading: .65em, spacing: .8em)
  set page(
    header: context [
      #set text(size: 8pt, fill: study-muted)
      #grid(columns: (1fr, auto), [#text(weight: "bold", fill: study-accent)[STUDY LAB] · #course], [#kind])
      #v(5pt)
      #line(length: 100%, stroke: .6pt + study-line)
    ],
    footer: context [
      #line(length: 100%, stroke: .6pt + study-line)
      #v(4pt)
      #grid(columns: (1fr, auto), text(size: 8pt, fill: study-muted)[#status],
        text(size: 8pt, fill: study-muted)[#counter(page).display("1") / #counter(page).final().first()])
    ],
  )
  show heading: it => {
    set text(fill: study-accent-strong)
    it
  }
  show link: set text(fill: study-accent-strong)
  set table(
    inset: (x: 7pt, y: 6pt),
    stroke: (x: none, y: .5pt + study-line),
    fill: (x, y) => if y == 0 { study-accent.lighten(93%) } else if calc.even(y) { study-soft } else { none },
  )
  show table.cell.where(y: 0): set text(weight: "bold", fill: study-accent-strong)
  body
}
