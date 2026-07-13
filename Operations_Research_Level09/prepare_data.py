from __future__ import annotations

import json
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests


API_URL = "https://blackbox-2d.onrender.com/evaluate"

LOWER_BOUND = -5.0
UPPER_BOUND = 5.0

DATA_DIR = Path("data")
FIGURE_DIR = Path("figures")
CACHE_FILE = DATA_DIR / "api_cache.json"

DATA_DIR.mkdir(exist_ok=True)
FIGURE_DIR.mkdir(exist_ok=True)


class Blackbox:
    """
    Zugriff auf die zweidimensionale Blackbox.

    Bereits abgefragte Punkte werden lokal gespeichert, damit beim
    erneuten Ausführen nicht dieselben Serveranfragen entstehen.
    """

    def __init__(self, cache_file: Path = CACHE_FILE):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.session = requests.Session()

    def _load_cache(self) -> dict[str, float]:
        if not self.cache_file.exists():
            return {}

        with self.cache_file.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _save_cache(self) -> None:
        with self.cache_file.open("w", encoding="utf-8") as file:
            json.dump(self.cache, file, indent=2, ensure_ascii=False)

    @staticmethod
    def _key(x: float, y: float) -> str:
        return f"{x:.8f},{y:.8f}"

    @staticmethod
    def _read_value(data: dict) -> float:
        """
        Berücksichtigt mehrere mögliche Namen des Ergebnisfeldes.
        """
        for field in ("result", "height", "value", "z"):
            if field in data:
                return float(data[field])

        numeric_values = [
            value for value in data.values() if isinstance(value, (int, float))
        ]

        if len(numeric_values) == 1:
            return float(numeric_values[0])

        raise ValueError(f"Die Serverantwort enthält kein erkennbares Ergebnis: {data}")

    def evaluate(self, x: float, y: float) -> float:
        x = float(np.clip(x, LOWER_BOUND, UPPER_BOUND))
        y = float(np.clip(y, LOWER_BOUND, UPPER_BOUND))

        key = self._key(x, y)

        if key in self.cache:
            return float(self.cache[key])

        last_error: Exception | None = None

        for attempt in range(5):
            try:
                response = self.session.get(
                    API_URL, params={"x": x, "y": y}, timeout=30
                )
                response.raise_for_status()

                value = self._read_value(response.json())

                self.cache[key] = value
                self._save_cache()

                # Kleine Pause, um den Server nicht unnötig zu belasten.
                time.sleep(0.03)

                return value

            except (requests.RequestException, ValueError, TypeError) as error:
                last_error = error
                wait_time = 2 * (attempt + 1)

                print(
                    f"Abfrage ({x:.4f}, {y:.4f}) fehlgeschlagen. "
                    f"Neuer Versuch in {wait_time} Sekunden."
                )

                time.sleep(wait_time)

        raise RuntimeError(
            f"Der Punkt ({x}, {y}) konnte nicht ausgewertet werden."
        ) from last_error


def exploratory_search(
    blackbox: Blackbox, point: np.ndarray, step: float
) -> tuple[np.ndarray, float]:
    """
    Explorative Koordinatensuche für ein Maximierungsproblem.

    In jeder Dimension werden der positive und der negative Schritt
    geprüft. Der jeweils beste Punkt wird übernommen.
    """
    current = np.array(point, dtype=float)
    current_value = blackbox.evaluate(*current)

    for dimension in range(2):
        candidates = [current.copy()]

        for direction in (-1, 1):
            candidate = current.copy()
            candidate[dimension] += direction * step
            candidate = np.clip(candidate, LOWER_BOUND, UPPER_BOUND)
            candidates.append(candidate)

        values = [blackbox.evaluate(*candidate) for candidate in candidates]

        best_index = int(np.argmax(values))
        current = candidates[best_index]
        current_value = values[best_index]

    return current, current_value


def hooke_jeeves(
    blackbox: Blackbox,
    start: tuple[float, float] | np.ndarray,
    run_name: str,
    initial_step: float = 1.0,
    tolerance: float = 0.001,
    max_iterations: int = 500,
) -> tuple[dict, list[dict]]:
    """
    Hooke-und-Jeeves-Mustersuche für ein Maximum.
    """
    base = np.array(start, dtype=float)
    base_value = blackbox.evaluate(*base)

    step = float(initial_step)
    iteration = 0

    history = [
        {
            "run": run_name,
            "iteration": iteration,
            "event": "Startpunkt",
            "x": base[0],
            "y": base[1],
            "height": base_value,
            "step": step,
        }
    ]

    while step >= tolerance and iteration < max_iterations:
        iteration += 1

        explored, explored_value = exploratory_search(blackbox, base, step)

        if explored_value <= base_value:
            step /= 2

            history.append(
                {
                    "run": run_name,
                    "iteration": iteration,
                    "event": "Schrittweite halbiert",
                    "x": base[0],
                    "y": base[1],
                    "height": base_value,
                    "step": step,
                }
            )
            continue

        previous_base = base.copy()
        base = explored
        base_value = explored_value

        history.append(
            {
                "run": run_name,
                "iteration": iteration,
                "event": "Exploration",
                "x": base[0],
                "y": base[1],
                "height": base_value,
                "step": step,
            }
        )

        while iteration < max_iterations:
            iteration += 1

            pattern_point = base + (base - previous_base)
            pattern_point = np.clip(pattern_point, LOWER_BOUND, UPPER_BOUND)

            pattern_candidate, pattern_value = exploratory_search(
                blackbox, pattern_point, step
            )

            if pattern_value > base_value:
                previous_base = base.copy()
                base = pattern_candidate
                base_value = pattern_value

                history.append(
                    {
                        "run": run_name,
                        "iteration": iteration,
                        "event": "Musterschritt",
                        "x": base[0],
                        "y": base[1],
                        "height": base_value,
                        "step": step,
                    }
                )
            else:
                break

    result = {
        "run": run_name,
        "start_x": float(start[0]),
        "start_y": float(start[1]),
        "x": float(base[0]),
        "y": float(base[1]),
        "height": float(base_value),
        "iterations": iteration,
        "final_step": step,
    }

    return result, history


def create_grid(blackbox: Blackbox, grid_size: int = 31) -> pd.DataFrame:
    """
    Grobe Gittersuche auf [-5, 5]^2.
    """
    xs = np.linspace(LOWER_BOUND, UPPER_BOUND, grid_size)
    ys = np.linspace(LOWER_BOUND, UPPER_BOUND, grid_size)

    rows = []
    total = grid_size * grid_size
    counter = 0

    for y in ys:
        for x in xs:
            counter += 1
            value = blackbox.evaluate(x, y)

            rows.append({"x": x, "y": y, "height": value})

            if counter % 50 == 0 or counter == total:
                print(f"Gittersuche: {counter}/{total}")

    return pd.DataFrame(rows)


def choose_multistarts(
    grid: pd.DataFrame, number: int = 8, minimum_distance: float = 1.0
) -> list[np.ndarray]:
    """
    Wählt hohe und räumlich hinreichend getrennte Gitterpunkte.
    """
    ordered = grid.sort_values("height", ascending=False)

    starts: list[np.ndarray] = []

    for row in ordered.itertuples():
        candidate = np.array([row.x, row.y])

        far_enough = all(
            np.linalg.norm(candidate - existing) >= minimum_distance
            for existing in starts
        )

        if far_enough:
            starts.append(candidate)

        if len(starts) == number:
            break

    return starts


def create_static_figures(
    grid: pd.DataFrame, paths: pd.DataFrame, summary: pd.DataFrame
) -> None:
    """
    Erstellt PDF-taugliche Matplotlib-Grafiken.
    """
    x_values = np.sort(grid["x"].unique())
    y_values = np.sort(grid["y"].unique())

    z_values = (
        grid.pivot(index="y", columns="x", values="height")
        .reindex(index=y_values, columns=x_values)
        .to_numpy()
    )

    x_grid, y_grid = np.meshgrid(x_values, y_values)

    required_runs = ["Start (2, -4)", "Start (0.2, -2)"]

    plt.figure(figsize=(8.5, 6.8))

    contours = plt.contourf(x_grid, y_grid, z_values, levels=30)

    plt.colorbar(contours, label="Höhe")

    for run_name in required_runs:
        run_path = paths[paths["run"] == run_name]

        plt.plot(
            run_path["x"],
            run_path["y"],
            marker="o",
            markersize=3,
            linewidth=1.3,
            label=run_name,
        )

        if not run_path.empty:
            plt.scatter(run_path.iloc[0]["x"], run_path.iloc[0]["y"], marker="s", s=65)

            plt.scatter(
                run_path.iloc[-1]["x"], run_path.iloc[-1]["y"], marker="*", s=180
            )

    best = summary.loc[summary["height"].idxmax()]

    plt.scatter(
        best["x"], best["y"], marker="*", s=240, label="Bester gefundener Punkt"
    )

    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Höhenkarte und Suchpfade")
    plt.xlim(LOWER_BOUND, UPPER_BOUND)
    plt.ylim(LOWER_BOUND, UPPER_BOUND)
    plt.legend()
    plt.tight_layout()

    plt.savefig(FIGURE_DIR / "contour_paths.pdf", bbox_inches="tight")
    plt.savefig(FIGURE_DIR / "contour_paths.png", dpi=220, bbox_inches="tight")
    plt.close()

    figure = plt.figure(figsize=(9, 7))
    axis = figure.add_subplot(projection="3d")

    axis.plot_surface(x_grid, y_grid, z_values, alpha=0.8)

    for run_name in required_runs:
        run_path = paths[paths["run"] == run_name]

        if not run_path.empty:
            axis.plot(
                run_path["x"],
                run_path["y"],
                run_path["height"],
                marker="o",
                label=run_name,
            )

    axis.set_xlabel("x")
    axis.set_ylabel("y")
    axis.set_zlabel("Höhe")
    axis.set_title("Dreidimensionales Höhenprofil")
    axis.legend()

    plt.tight_layout()

    plt.savefig(FIGURE_DIR / "surface_paths.pdf", bbox_inches="tight")
    plt.savefig(FIGURE_DIR / "surface_paths.png", dpi=220, bbox_inches="tight")
    plt.close()


def main() -> None:
    blackbox = Blackbox()

    print("Erstelle grobes Höhenraster.")
    grid = create_grid(blackbox, grid_size=31)
    grid.to_csv(DATA_DIR / "grid.csv", index=False)

    required_starts = [((2.0, -4.0), "Start (2, -4)"), ((0.2, -2.0), "Start (0.2, -2)")]

    results = []
    histories = []

    print("Starte die vorgeschriebenen Suchläufe.")

    for start, run_name in required_starts:
        result, history = hooke_jeeves(
            blackbox, start=start, run_name=run_name, initial_step=1.0, tolerance=0.001
        )

        results.append(result)
        histories.extend(history)

    print("Wähle zusätzliche Startpunkte aus dem Höhenraster.")

    multistarts = choose_multistarts(grid, number=8, minimum_distance=1.0)

    for index, start in enumerate(multistarts, start=1):
        run_name = f"Multi-Start {index}"

        result, history = hooke_jeeves(
            blackbox, start=start, run_name=run_name, initial_step=0.5, tolerance=0.001
        )

        results.append(result)
        histories.extend(history)

    summary = pd.DataFrame(results)
    paths = pd.DataFrame(histories)

    summary.to_csv(DATA_DIR / "summary.csv", index=False)
    paths.to_csv(DATA_DIR / "paths.csv", index=False)

    create_static_figures(grid, paths, summary)

    best = summary.loc[summary["height"].idxmax()]

    print()
    print("Bester gefundener Punkt:")
    print(f"x = {best['x']:.6f}")
    print(f"y = {best['y']:.6f}")
    print(f"Höhe = {best['height']:.8f}")
    print()
    print("Die Daten und Grafiken wurden gespeichert.")


if __name__ == "__main__":
    main()
