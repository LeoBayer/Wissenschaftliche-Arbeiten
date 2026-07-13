# Operations Research – Level 9

Zweidimensionale Blackbox-Optimierung für Operations Research im
Sommersemester 2026.

## Gruppe 42

- Benit Meise
- Jakob Wiemer
- Leo Bayer

## Installation

```bash
python3 -m pip install -r requirements.txt
```

Zusätzlich müssen Quarto und eine LaTeX-Distribution installiert sein.

## Daten erzeugen

```bash
python3 prepare_data.py
```

Das Skript erzeugt:

```text
data/grid.csv
data/paths.csv
data/summary.csv
figures/contour_paths.pdf
figures/contour_paths.png
figures/surface_paths.pdf
figures/surface_paths.png
```

## Website lokal ansehen

```bash
quarto preview
```

## Website rendern

```bash
quarto render
```

Die GitHub-Pages-Dateien werden in `docs/` gespeichert.

## PDF erzeugen

```bash
quarto render report.qmd --to pdf
```

Abhängig von der Quarto-Konfiguration befindet sich die PDF anschließend
als `docs/report.pdf`.

## GitHub Pages

Unter

```text
Settings → Pages
```

wird ausgewählt:

```text
Source: Deploy from a branch
Branch: main
Folder: /docs
```

Danach ist die Website unter folgender Struktur erreichbar:

```text
https://DEIN-GITHUB-NAME.github.io/DEIN-REPOSITORY/
```
