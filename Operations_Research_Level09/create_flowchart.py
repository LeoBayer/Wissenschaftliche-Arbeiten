from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch


OUTPUT_DIR = Path("figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def add_step(
    axis,
    center_y: float,
    facecolor: str,
    edgecolor: str,
) -> None:
    """
    Zeichnet einen nummerierten Prozessschritt.
    """
    box_x = 0.08
    box_width = 0.84
    box_height = 0.105
    box_bottom = center_y - box_height / 2

    box = FancyBboxPatch(
        (box_x, box_bottom),
        box_width,
        box_height,
        boxstyle="round,pad=0.015,rounding_size=0.025",
        linewidth=1.1,
        facecolor=facecolor,
        edgecolor=edgecolor,
    )
    axis.add_patch(box)


def add_arrow(
    axis,
    upper_y: float,
    lower_y: float,
) -> None:
    """
    Zeichnet einen vertikalen Pfeil zwischen zwei Prozessschritten.
    """
    axis.annotate(
        "",
        xy=(0.50, lower_y + 0.061),
        xytext=(0.50, upper_y - 0.061),
        arrowprops={
            "arrowstyle": "-|>",
            "linewidth": 1.1,
            "color": "#485563",
        },
    )


def create_flowchart() -> None:
    """
    Erstellt ein kompaktes vertikales Flussdiagramm für die PDF.
    """
    figure, axis = plt.subplots(figsize=(5.1, 7.2))

    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")

    steps = [
        (
            1,
            0.88,
            "Blackbox über API auswerten\nund Ergebnisse lokal speichern",
            "#edf4fc",
            "#315f9b",
        ),
        (
            2,
            0.73,
            "Grobes Raster auf $[-5,5]^2$\nerzeugen und auswerten",
            "#eef7ed",
            "#38834a",
        ),
        (
            3,
            0.58,
            "Hohe und räumlich getrennte\nStartpunkte auswählen",
            "#fff6e8",
            "#df941c",
        ),
        (
            4,
            0.43,
            "Hooke-und-Jeeves-Suche\nvon jedem Startpunkt durchführen",
            "#f3eef9",
            "#674095",
        ),
        (
            5,
            0.28,
            "Endpunkte aller Suchläufe\nmiteinander vergleichen",
            "#edf4fc",
            "#315f9b",
        ),
        (
            6,
            0.13,
            "Höchsten gefundenen Punkt\nals Ergebnis ausgeben",
            "#eef7ed",
            "#38834a",
        ),
    ]

    for number, y, text, facecolor, edgecolor in steps:
        add_step(
            axis=axis,
            center_y=y,
            facecolor=facecolor,
            edgecolor=edgecolor,
        )

    for current, following in zip(steps, steps[1:]):
        add_arrow(
            axis=axis,
            upper_y=current[1],
            lower_y=following[1],
        )

    axis.set_title(
        "Ablauf der kombinierten Blackbox-Suche",
        fontsize=11.5,
        fontweight="semibold",
        pad=8,
        color="#315f9b",
    )

    figure.tight_layout(pad=0.25)

    figure.savefig(
        OUTPUT_DIR / "workflow_vertical.pdf",
        bbox_inches="tight",
    )

    figure.savefig(
        OUTPUT_DIR / "workflow_vertical.png",
        dpi=240,
        bbox_inches="tight",
    )

    plt.close(figure)

    print("Erzeugt:")
    print(OUTPUT_DIR / "workflow_vertical.pdf")
    print(OUTPUT_DIR / "workflow_vertical.png")


if __name__ == "__main__":
    create_flowchart()
