from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


LOWER_BOUND = -5.0
UPPER_BOUND = 5.0

FIGURE_DIR = Path("figures")

REQUIRED_RUNS = [
    "Start (2, -4)",
    "Start (0.2, -2)",
]


def load_data(
    data_dir: Path | str = "data/processed",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Lädt Raster, Suchverläufe und Ergebnisübersicht.
    """
    data_dir = Path(data_dir)

    grid_file = data_dir / "grid.csv"
    paths_file = data_dir / "paths.csv"
    summary_file = data_dir / "summary.csv"

    missing = [
        str(path)
        for path in (
            grid_file,
            paths_file,
            summary_file,
        )
        if not path.exists()
    ]

    if missing:
        raise FileNotFoundError(
            "Es fehlen Ergebnisdateien. "
            "Führe zuerst prepare_data.py aus. "
            f"Fehlend: {missing}"
        )

    grid = pd.read_csv(grid_file)
    paths = pd.read_csv(paths_file)
    summary = pd.read_csv(summary_file)

    return grid, paths, summary


def prepare_grid(
    grid: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Wandelt die Rastertabelle in x-, y- und z-Matrizen um.
    """
    x_values = np.sort(grid["x"].unique())

    y_values = np.sort(grid["y"].unique())

    z_values = (
        grid.pivot(
            index="y",
            columns="x",
            values="height",
        )
        .reindex(
            index=y_values,
            columns=x_values,
        )
        .to_numpy()
    )

    return x_values, y_values, z_values


def accepted_path(
    paths: pd.DataFrame,
    run_name: str,
) -> pd.DataFrame:
    """
    Gibt die akzeptierten Punkte eines Suchlaufs zurück.

    Einträge zur reinen Schrittweitenhalbierung werden ausgeschlossen,
    weil sich dabei die Position nicht verändert.
    """
    run = paths[
        (paths["run"] == run_name)
        & (paths["accepted"] == True)
        & (paths["event"] != "Schrittweite halbiert")
    ].copy()

    run = run.sort_values(["iteration"])

    return run


def create_static_contour(
    grid: pd.DataFrame,
    paths: pd.DataFrame,
    summary: pd.DataFrame,
    output_file: Path | str = FIGURE_DIR / "contour_paths.pdf",
) -> None:
    """
    Erzeugt eine statische Konturkarte für die PDF.
    """
    output_file = Path(output_file)
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    x_values, y_values, z_values = prepare_grid(grid)
    x_grid, y_grid = np.meshgrid(
        x_values,
        y_values,
    )

    best = summary.loc[summary["height"].idxmax()]

    plt.figure(figsize=(8.5, 6.8))

    contours = plt.contourf(
        x_grid,
        y_grid,
        z_values,
        levels=30,
    )

    plt.contour(
        x_grid,
        y_grid,
        z_values,
        levels=15,
        linewidths=0.5,
    )

    plt.colorbar(
        contours,
        label="Höhe",
    )

    for run_name in REQUIRED_RUNS:
        run = accepted_path(
            paths,
            run_name,
        )

        if run.empty:
            continue

        plt.plot(
            run["x"],
            run["y"],
            marker="o",
            markersize=4,
            linewidth=1.5,
            label=run_name,
        )

        plt.scatter(
            run.iloc[0]["x"],
            run.iloc[0]["y"],
            marker="s",
            s=70,
        )

        plt.scatter(
            run.iloc[-1]["x"],
            run.iloc[-1]["y"],
            marker="*",
            s=180,
        )

    plt.scatter(
        best["x"],
        best["y"],
        marker="*",
        s=250,
        label="Bester gefundener Punkt",
    )

    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Höhenkarte und akzeptierte Suchschritte")

    plt.xlim(
        LOWER_BOUND,
        UPPER_BOUND,
    )
    plt.ylim(
        LOWER_BOUND,
        UPPER_BOUND,
    )

    plt.legend()
    plt.tight_layout()

    plt.savefig(
        output_file,
        bbox_inches="tight",
    )

    if output_file.suffix.lower() != ".png":
        plt.savefig(
            output_file.with_suffix(".png"),
            dpi=220,
            bbox_inches="tight",
        )

    plt.close()


def create_static_surface(
    grid: pd.DataFrame,
    paths: pd.DataFrame,
    output_file: Path | str = FIGURE_DIR / "surface_paths.pdf",
) -> None:
    """
    Erzeugt eine statische 3D-Oberfläche für die PDF.
    """
    output_file = Path(output_file)
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    x_values, y_values, z_values = prepare_grid(grid)
    x_grid, y_grid = np.meshgrid(
        x_values,
        y_values,
    )

    figure = plt.figure(figsize=(9, 7))

    axis = figure.add_subplot(projection="3d")

    axis.plot_surface(
        x_grid,
        y_grid,
        z_values,
        alpha=0.8,
    )

    for run_name in REQUIRED_RUNS:
        run = accepted_path(
            paths,
            run_name,
        )

        if run.empty:
            continue

        axis.plot(
            run["x"],
            run["y"],
            run["height"],
            marker="o",
            label=run_name,
        )

    axis.set_xlabel("x")
    axis.set_ylabel("y")
    axis.set_zlabel("Höhe")

    axis.set_title("Dreidimensionales Höhenprofil")

    axis.legend()

    plt.tight_layout()

    plt.savefig(
        output_file,
        bbox_inches="tight",
    )

    if output_file.suffix.lower() != ".png":
        plt.savefig(
            output_file.with_suffix(".png"),
            dpi=220,
            bbox_inches="tight",
        )

    plt.close()


def create_static_result_comparison(
    summary: pd.DataFrame,
    output_file: Path | str = FIGURE_DIR / "result_comparison.pdf",
) -> None:
    """
    Vergleicht die Höhenwerte aller lokalen Suchläufe.
    """
    output_file = Path(output_file)
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    ordered = summary.sort_values(
        "height",
        ascending=True,
    )

    plt.figure(figsize=(8.5, 5.5))

    plt.barh(
        ordered["run"],
        ordered["height"],
    )

    plt.xlabel("Gefundene Höhe")
    plt.ylabel("Suchlauf")

    plt.title("Vergleich der gefundenen lokalen Maxima")

    plt.tight_layout()

    plt.savefig(
        output_file,
        bbox_inches="tight",
    )

    if output_file.suffix.lower() != ".png":
        plt.savefig(
            output_file.with_suffix(".png"),
            dpi=220,
            bbox_inches="tight",
        )

    plt.close()


def create_interactive_surface(
    grid: pd.DataFrame,
    paths: pd.DataFrame,
    summary: pd.DataFrame,
) -> go.Figure:
    """
    Erzeugt eine interaktive Plotly-3D-Oberfläche.
    """
    x_values, y_values, z_values = prepare_grid(grid)

    best = summary.loc[summary["height"].idxmax()]

    figure = go.Figure()

    figure.add_trace(
        go.Surface(
            x=x_values,
            y=y_values,
            z=z_values,
            name="Höhenfläche",
            colorbar={
                "title": "Höhe",
            },
            hovertemplate=(
                "x: %{x:.3f}<br>y: %{y:.3f}<br>Höhe: %{z:.6f}<extra></extra>"
            ),
        )
    )

    for run_name in REQUIRED_RUNS:
        run = accepted_path(
            paths,
            run_name,
        )

        if run.empty:
            continue

        customdata = np.column_stack(
            (
                run["iteration"],
                run["step"],
                run["event"],
            )
        )

        figure.add_trace(
            go.Scatter3d(
                x=run["x"],
                y=run["y"],
                z=run["height"],
                mode="lines+markers",
                name=run_name,
                customdata=customdata,
                hovertemplate=(
                    "%{customdata[2]}<br>"
                    "Iteration: %{customdata[0]}<br>"
                    "Schrittweite: %{customdata[1]:.5f}<br>"
                    "x: %{x:.5f}<br>"
                    "y: %{y:.5f}<br>"
                    "Höhe: %{z:.7f}"
                    "<extra></extra>"
                ),
            )
        )

    figure.add_trace(
        go.Scatter3d(
            x=[best["x"]],
            y=[best["y"]],
            z=[best["height"]],
            mode="markers",
            marker={
                "size": 8,
                "symbol": "diamond",
            },
            name="Bester gefundener Punkt",
            hovertemplate=(
                "Bester gefundener Punkt<br>"
                "x: %{x:.6f}<br>"
                "y: %{y:.6f}<br>"
                "Höhe: %{z:.8f}"
                "<extra></extra>"
            ),
        )
    )

    figure.update_layout(
        title=("Interaktive dreidimensionale Höhenlandschaft"),
        scene={
            "xaxis_title": "x",
            "yaxis_title": "y",
            "zaxis_title": "Höhe",
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
        },
        margin={
            "l": 0,
            "r": 0,
            "b": 0,
            "t": 80,
        },
    )

    return figure


def create_interactive_contour(
    grid: pd.DataFrame,
    paths: pd.DataFrame,
    summary: pd.DataFrame,
) -> go.Figure:
    """
    Erzeugt eine interaktive Konturkarte mit den akzeptierten
    Suchpfaden der vorgeschriebenen Startpunkte.
    """
    x_values, y_values, z_values = prepare_grid(grid)

    best = summary.loc[summary["height"].idxmax()]

    figure = go.Figure()

    # Höhenlandschaft als Konturkarte
    figure.add_trace(
        go.Contour(
            x=x_values,
            y=y_values,
            z=z_values,
            name="Höhenlandschaft",
            showscale=True,
            contours={
                "coloring": "heatmap",
                "showlabels": True,
                "labelfont": {
                    "size": 11,
                },
            },
            colorbar={
                "title": {
                    "text": "Höhe",
                },
                "thickness": 30,
                "len": 0.88,
                "y": 0.48,
            },
            hovertemplate=(
                "x: %{x:.3f}<br>y: %{y:.3f}<br>Höhe: %{z:.6f}<extra></extra>"
            ),
        )
    )

    # Akzeptierte Pfade der vorgeschriebenen Suchläufe
    for run_name in REQUIRED_RUNS:
        run = accepted_path(
            paths=paths,
            run_name=run_name,
        )

        if run.empty:
            continue

        customdata = np.column_stack(
            (
                run["iteration"],
                run["height"],
                run["step"],
                run["event"],
            )
        )

        figure.add_trace(
            go.Scatter(
                x=run["x"],
                y=run["y"],
                mode="lines+markers",
                name=run_name,
                customdata=customdata,
                line={
                    "width": 2,
                },
                marker={
                    "size": 8,
                },
                hovertemplate=(
                    "%{customdata[3]}<br>"
                    "Iteration: %{customdata[0]}<br>"
                    "x: %{x:.5f}<br>"
                    "y: %{y:.5f}<br>"
                    "Höhe: %{customdata[1]:.7f}<br>"
                    "Schrittweite: %{customdata[2]:.5f}"
                    "<extra></extra>"
                ),
            )
        )

    # Bester insgesamt gefundener Punkt
    figure.add_trace(
        go.Scatter(
            x=[best["x"]],
            y=[best["y"]],
            mode="markers",
            name="Bester gefundener Punkt",
            marker={
                "size": 17,
                "symbol": "star",
            },
            hovertemplate=(
                "Bester gefundener Punkt<br>"
                "x: %{x:.6f}<br>"
                "y: %{y:.6f}<br>"
                f"Höhe: {best['height']:.8f}"
                "<extra></extra>"
            ),
        )
    )

    # Layout analog zur funktionierenden 3D-Grafik
    figure.update_layout(
        title=dict(
            text="Interaktive Konturkarte mit Suchpfaden",
            x=0.5,
            xanchor="center",
        ),
        width=1000,
        height=780,
        margin=dict(
            l=40,
            r=40,
            b=40,
            t=120,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.85)",
        ),
    )
    return figure


def create_search_animation(
    paths: pd.DataFrame,
) -> go.Figure:
    """
    Erzeugt eine Animation der akzeptierten Suchpunkte.
    """
    accepted = paths[
        (paths["run"].isin(REQUIRED_RUNS))
        & (paths["accepted"] == True)
        & (paths["event"] != "Schrittweite halbiert")
    ].copy()

    accepted = accepted.sort_values(
        [
            "run",
            "iteration",
        ]
    )

    accepted["frame"] = accepted.groupby("run").cumcount()

    figure = px.scatter(
        accepted,
        x="x",
        y="y",
        animation_frame="frame",
        animation_group="run",
        color="run",
        hover_name="event",
        hover_data={
            "height": ":.7f",
            "step": ":.5f",
            "iteration": True,
            "frame": False,
        },
        range_x=[
            LOWER_BOUND,
            UPPER_BOUND,
        ],
        range_y=[
            LOWER_BOUND,
            UPPER_BOUND,
        ],
        title=("Entwicklung der akzeptierten Suchpunkte"),
    )

    figure.update_traces(
        marker={
            "size": 14,
        }
    )

    figure.update_layout(
        xaxis_title="x",
        yaxis_title="y",
        legend_title="Suchlauf",
    )

    return figure


def create_evaluation_scatter(
    paths: pd.DataFrame,
) -> go.Figure:
    """
    Zeigt alle geprüften Punkte und unterscheidet zwischen akzeptierten
    und verworfenen Kandidaten.
    """
    selected = paths[paths["run"].isin(REQUIRED_RUNS)].copy()

    selected["status"] = np.where(
        selected["accepted"],
        "Akzeptiert",
        "Verworfen",
    )

    figure = px.scatter(
        selected,
        x="x",
        y="y",
        color="status",
        symbol="run",
        hover_name="event",
        hover_data={
            "height": ":.7f",
            "step": ":.5f",
            "iteration": True,
            "accepted": False,
        },
        range_x=[
            LOWER_BOUND,
            UPPER_BOUND,
        ],
        range_y=[
            LOWER_BOUND,
            UPPER_BOUND,
        ],
        title=("Alle untersuchten Punkte der vorgeschriebenen Suchläufe"),
    )

    figure.update_layout(
        xaxis_title="x",
        yaxis_title="y",
    )

    return figure


def create_all_static_figures() -> None:
    """
    Lädt die Ergebnisdaten und erzeugt alle PDF-tauglichen Grafiken.
    """
    grid, paths, summary = load_data()

    FIGURE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    create_static_contour(
        grid=grid,
        paths=paths,
        summary=summary,
    )

    create_static_surface(
        grid=grid,
        paths=paths,
    )

    create_static_result_comparison(
        summary=summary,
    )

    print("Statische Grafiken wurden erzeugt:")

    for file in sorted(FIGURE_DIR.glob("*")):
        print(file)


if __name__ == "__main__":
    create_all_static_figures()
