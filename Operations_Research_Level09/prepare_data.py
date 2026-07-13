from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from src.api import BlackBox2D
from src.optimization import SearchResult, hooke_jeeves


LOWER_BOUND = -5.0
UPPER_BOUND = 5.0

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

GRID_FILE = PROCESSED_DIR / "grid.csv"
PATHS_FILE = PROCESSED_DIR / "paths.csv"
SUMMARY_FILE = PROCESSED_DIR / "summary.csv"
METADATA_FILE = PROCESSED_DIR / "metadata.json"


def create_grid(
    blackbox: BlackBox2D,
    grid_size: int,
) -> pd.DataFrame:
    """
    Wertet ein gleichmäßiges Raster auf [-5, 5]^2 aus.

    Die Gittersuche dient zur groben Erkundung des gesamten Suchraums
    und zur Auswahl zusätzlicher Startpunkte.
    """
    if grid_size < 3:
        raise ValueError("Die Gittergröße muss mindestens 3 betragen.")

    x_values = np.linspace(
        LOWER_BOUND,
        UPPER_BOUND,
        grid_size,
    )
    y_values = np.linspace(
        LOWER_BOUND,
        UPPER_BOUND,
        grid_size,
    )

    rows: list[dict] = []

    total = grid_size * grid_size
    completed = 0

    for y in y_values:
        for x in x_values:
            completed += 1

            height = blackbox.evaluate(
                float(x),
                float(y),
            )

            rows.append(
                {
                    "x": float(x),
                    "y": float(y),
                    "height": float(height),
                }
            )

            if completed % 25 == 0 or completed == total:
                print(f"Gittersuche: {completed}/{total}")

    return pd.DataFrame(rows)


def select_multistarts(
    grid: pd.DataFrame,
    number_of_starts: int,
    minimum_distance: float,
) -> list[np.ndarray]:
    """
    Wählt hohe und räumlich getrennte Punkte aus dem Raster.

    Dadurch werden nicht mehrere fast identische Startpunkte auf
    demselben Gipfel verwendet.
    """
    if number_of_starts < 1:
        return []

    ordered_grid = grid.sort_values(
        "height",
        ascending=False,
    )

    selected: list[np.ndarray] = []

    for row in ordered_grid.itertuples():
        candidate = np.array(
            [row.x, row.y],
            dtype=float,
        )

        sufficiently_far = all(
            np.linalg.norm(candidate - point) >= minimum_distance for point in selected
        )

        if sufficiently_far:
            selected.append(candidate)

        if len(selected) >= number_of_starts:
            break

    return selected


def result_to_summary_row(
    result: SearchResult,
) -> dict:
    """
    Wandelt das Ergebnis eines Suchlaufs in eine Tabellenzeile um.
    """
    return {
        "run": result.run,
        "start_x": result.start_x,
        "start_y": result.start_y,
        "x": result.x,
        "y": result.y,
        "height": result.height,
        "iterations": result.iterations,
        "final_step": result.final_step,
        "evaluations": result.evaluations,
    }


def result_to_history_rows(
    result: SearchResult,
) -> list[dict]:
    """
    Wandelt den Suchverlauf eines Ergebnisses in Tabellenzeilen um.
    """
    return [asdict(evaluation) for evaluation in result.history]


def run_search(
    blackbox: BlackBox2D,
    start: tuple[float, float] | np.ndarray,
    run_name: str,
    initial_step: float,
    tolerance: float,
    max_iterations: int,
) -> SearchResult:
    """
    Führt einen Suchlauf aus und gibt eine kurze Zusammenfassung aus.
    """
    print()
    print(f"Starte: {run_name}")
    print(f"Startpunkt: ({float(start[0]):.4f}, {float(start[1]):.4f})")

    result = hooke_jeeves(
        blackbox=blackbox,
        start=start,
        run_name=run_name,
        initial_step=initial_step,
        tolerance=tolerance,
        max_iterations=max_iterations,
    )

    print(f"Endpunkt: ({result.x:.6f}, {result.y:.6f})")
    print(f"Höhe: {result.height:.8f}")
    print(f"Iterationen: {result.iterations}")
    print(f"Protokolleinträge: {result.evaluations}")

    return result


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=("Erzeugt die Daten für die zweidimensionale Blackbox-Optimierung.")
    )

    parser.add_argument(
        "--grid-size",
        type=int,
        default=21,
        help=("Anzahl der Rasterpunkte je Dimension. Standard: 21."),
    )

    parser.add_argument(
        "--multistarts",
        type=int,
        default=6,
        help=("Anzahl zusätzlicher Multi-Start-Läufe. Standard: 6."),
    )

    parser.add_argument(
        "--minimum-distance",
        type=float,
        default=1.0,
        help=("Mindestabstand zwischen Multi-Start-Punkten. Standard: 1.0."),
    )

    parser.add_argument(
        "--initial-step",
        type=float,
        default=1.0,
        help=("Anfangsschrittweite der vorgeschriebenen Suchläufe. Standard: 1.0."),
    )

    parser.add_argument(
        "--multistart-step",
        type=float,
        default=0.5,
        help=("Anfangsschrittweite der zusätzlichen Suchläufe. Standard: 0.5."),
    )

    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.001,
        help=("Abbruchtoleranz für die Schrittweite. Standard: 0.001."),
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=500,
        help=("Maximale Iterationszahl je Suchlauf. Standard: 500."),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )
    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    blackbox = BlackBox2D()

    try:
        print("Erzeuge grobes Höhenraster.")
        print(f"Gittergröße: {args.grid_size} x {args.grid_size}")

        grid = create_grid(
            blackbox=blackbox,
            grid_size=args.grid_size,
        )

        grid.to_csv(
            GRID_FILE,
            index=False,
        )

        print()
        print(f"Raster gespeichert: {GRID_FILE}")

        required_starts = [
            (
                (2.0, -4.0),
                "Start (2, -4)",
            ),
            (
                (0.2, -2.0),
                "Start (0.2, -2)",
            ),
        ]

        results: list[SearchResult] = []

        for start, run_name in required_starts:
            result = run_search(
                blackbox=blackbox,
                start=start,
                run_name=run_name,
                initial_step=args.initial_step,
                tolerance=args.tolerance,
                max_iterations=args.max_iterations,
            )

            results.append(result)

        selected_starts = select_multistarts(
            grid=grid,
            number_of_starts=args.multistarts,
            minimum_distance=args.minimum_distance,
        )

        print()
        print("Ausgewählte zusätzliche Startpunkte:")

        for index, point in enumerate(
            selected_starts,
            start=1,
        ):
            print(f"{index}: ({point[0]:.4f}, {point[1]:.4f})")

        for index, start in enumerate(
            selected_starts,
            start=1,
        ):
            result = run_search(
                blackbox=blackbox,
                start=start,
                run_name=f"Multi-Start {index}",
                initial_step=args.multistart_step,
                tolerance=args.tolerance,
                max_iterations=args.max_iterations,
            )

            results.append(result)

        summary_rows = [result_to_summary_row(result) for result in results]

        history_rows = []

        for result in results:
            history_rows.extend(result_to_history_rows(result))

        summary = pd.DataFrame(summary_rows)
        paths = pd.DataFrame(history_rows)

        summary = summary.sort_values(
            "height",
            ascending=False,
        ).reset_index(drop=True)

        summary.to_csv(
            SUMMARY_FILE,
            index=False,
        )

        paths.to_csv(
            PATHS_FILE,
            index=False,
        )

        best = summary.iloc[0]

        metadata = {
            "grid_size": args.grid_size,
            "grid_points": len(grid),
            "number_of_runs": len(results),
            "number_of_history_entries": len(paths),
            "cached_api_points": blackbox.cached_points(),
            "tolerance": args.tolerance,
            "best_point": {
                "x": float(best["x"]),
                "y": float(best["y"]),
                "height": float(best["height"]),
                "run": str(best["run"]),
            },
        }

        with METADATA_FILE.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                metadata,
                file,
                indent=2,
                ensure_ascii=False,
            )

        print()
        print("Datenerzeugung abgeschlossen.")
        print(f"Zusammenfassung: {SUMMARY_FILE}")
        print(f"Suchverläufe: {PATHS_FILE}")
        print(f"Metadaten: {METADATA_FILE}")

        print()
        print("Bester gefundener Punkt")
        print("-----------------------")
        print(f"Lauf: {best['run']}")
        print(f"x = {best['x']:.6f}")
        print(f"y = {best['y']:.6f}")
        print(f"Höhe = {best['height']:.8f}")

    finally:
        blackbox.close()


if __name__ == "__main__":
    main()
