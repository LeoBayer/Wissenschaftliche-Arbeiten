from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.api import BlackBox2D


LOWER_BOUND = -5.0
UPPER_BOUND = 5.0


@dataclass
class Evaluation:
    """
    Speichert eine einzelne Auswertung der Blackbox.
    """

    run: str
    iteration: int
    event: str
    accepted: bool
    x: float
    y: float
    height: float
    step: float


@dataclass
class SearchResult:
    """
    Zusammenfassung eines vollständigen Suchlaufs.
    """

    run: str
    start_x: float
    start_y: float
    x: float
    y: float
    height: float
    iterations: int
    final_step: float
    evaluations: int
    history: list[Evaluation]


def clip_point(point: np.ndarray) -> np.ndarray:
    """
    Begrenzt einen Punkt auf das zulässige Gebiet [-5, 5]^2.
    """
    return np.clip(
        np.asarray(point, dtype=float),
        LOWER_BOUND,
        UPPER_BOUND,
    )


def same_point(
    first: np.ndarray,
    second: np.ndarray,
    tolerance: float = 1e-12,
) -> bool:
    """
    Prüft, ob zwei Punkte numerisch gleich sind.
    """
    return bool(
        np.allclose(
            first,
            second,
            atol=tolerance,
            rtol=0.0,
        )
    )


def evaluate_candidate(
    blackbox: BlackBox2D,
    point: np.ndarray,
    run_name: str,
    iteration: int,
    event: str,
    accepted: bool,
    step: float,
    history: list[Evaluation],
) -> float:
    """
    Wertet einen Punkt aus und speichert ihn im Suchverlauf.
    """
    point = clip_point(point)
    value = blackbox.evaluate(
        point[0],
        point[1],
    )

    history.append(
        Evaluation(
            run=run_name,
            iteration=iteration,
            event=event,
            accepted=accepted,
            x=float(point[0]),
            y=float(point[1]),
            height=float(value),
            step=float(step),
        )
    )

    return float(value)


def exploratory_search(
    blackbox: BlackBox2D,
    base_point: np.ndarray,
    base_value: float,
    step: float,
    run_name: str,
    iteration: int,
    history: list[Evaluation],
) -> tuple[np.ndarray, float, bool]:
    """
    Führt einen explorativen Koordinatenschritt durch.

    Für jede Dimension wird zuerst die positive und anschließend
    gegebenenfalls die negative Richtung geprüft. Eine Verbesserung
    wird direkt als neuer Zwischenpunkt übernommen.
    """
    current = clip_point(base_point)
    current_value = float(base_value)
    improved = False

    for dimension in range(2):
        positive = current.copy()
        positive[dimension] += step
        positive = clip_point(positive)

        positive_value = evaluate_candidate(
            blackbox=blackbox,
            point=positive,
            run_name=run_name,
            iteration=iteration,
            event=f"Exploration + Dimension {dimension + 1}",
            accepted=False,
            step=step,
            history=history,
        )

        if positive_value > current_value:
            history[-1].accepted = True
            current = positive
            current_value = positive_value
            improved = True
            continue

        negative = current.copy()
        negative[dimension] -= step
        negative = clip_point(negative)

        negative_value = evaluate_candidate(
            blackbox=blackbox,
            point=negative,
            run_name=run_name,
            iteration=iteration,
            event=f"Exploration - Dimension {dimension + 1}",
            accepted=False,
            step=step,
            history=history,
        )

        if negative_value > current_value:
            history[-1].accepted = True
            current = negative
            current_value = negative_value
            improved = True

    return current, current_value, improved


def hooke_jeeves(
    blackbox: BlackBox2D,
    start: tuple[float, float] | np.ndarray,
    run_name: str,
    initial_step: float = 1.0,
    tolerance: float = 0.001,
    max_iterations: int = 500,
) -> SearchResult:
    """
    Hooke-und-Jeeves-Mustersuche für ein Maximierungsproblem.

    Ablauf:
    1. Explorative Suche um den aktuellen Basispunkt.
    2. Bei Verbesserung wird ein Musterschritt durchgeführt.
    3. Ohne Verbesserung wird die Schrittweite halbiert.
    4. Abbruch bei Unterschreiten der Toleranz.
    """
    if initial_step <= 0:
        raise ValueError("Die Anfangsschrittweite muss positiv sein.")

    if tolerance <= 0:
        raise ValueError("Die Toleranz muss positiv sein.")

    if max_iterations <= 0:
        raise ValueError("Die maximale Iterationszahl muss positiv sein.")

    base = clip_point(np.asarray(start, dtype=float))

    if base.shape != (2,):
        raise ValueError("Der Startpunkt muss genau zwei Koordinaten besitzen.")

    history: list[Evaluation] = []

    base_value = evaluate_candidate(
        blackbox=blackbox,
        point=base,
        run_name=run_name,
        iteration=0,
        event="Startpunkt",
        accepted=True,
        step=initial_step,
        history=history,
    )

    step = float(initial_step)
    iteration = 0

    while step >= tolerance and iteration < max_iterations:
        iteration += 1

        explored, explored_value, improved = exploratory_search(
            blackbox=blackbox,
            base_point=base,
            base_value=base_value,
            step=step,
            run_name=run_name,
            iteration=iteration,
            history=history,
        )

        if not improved:
            step /= 2

            history.append(
                Evaluation(
                    run=run_name,
                    iteration=iteration,
                    event="Schrittweite halbiert",
                    accepted=True,
                    x=float(base[0]),
                    y=float(base[1]),
                    height=float(base_value),
                    step=float(step),
                )
            )
            continue

        previous_base = base.copy()
        base = explored
        base_value = explored_value

        while iteration < max_iterations:
            iteration += 1

            pattern_point = base + (base - previous_base)
            pattern_point = clip_point(pattern_point)

            pattern_value = evaluate_candidate(
                blackbox=blackbox,
                point=pattern_point,
                run_name=run_name,
                iteration=iteration,
                event="Musterschritt",
                accepted=False,
                step=step,
                history=history,
            )

            explored_pattern, explored_pattern_value, pattern_improved = (
                exploratory_search(
                    blackbox=blackbox,
                    base_point=pattern_point,
                    base_value=pattern_value,
                    step=step,
                    run_name=run_name,
                    iteration=iteration,
                    history=history,
                )
            )

            if pattern_improved and explored_pattern_value > base_value:
                history[-1].accepted = True
                previous_base = base.copy()
                base = explored_pattern
                base_value = explored_pattern_value
                continue

            if pattern_value > base_value:
                for evaluation in reversed(history):
                    if (
                        evaluation.iteration == iteration
                        and evaluation.event == "Musterschritt"
                    ):
                        evaluation.accepted = True
                        break

                previous_base = base.copy()
                base = pattern_point
                base_value = pattern_value
                continue

            break

    return SearchResult(
        run=run_name,
        start_x=float(start[0]),
        start_y=float(start[1]),
        x=float(base[0]),
        y=float(base[1]),
        height=float(base_value),
        iterations=iteration,
        final_step=float(step),
        evaluations=len(history),
        history=history,
    )
