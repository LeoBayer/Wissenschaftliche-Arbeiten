from __future__ import annotations

import json
import time
from pathlib import Path

import requests


API_URL = "https://blackbox-2d.onrender.com/evaluate"

LOWER_BOUND = -5.0
UPPER_BOUND = 5.0

CACHE_FILE = Path("data/raw/api_cache.json")


class BlackBox2D:
    """
    Zugriff auf die zweidimensionale Höhen-Blackbox.

    Bereits abgefragte Punkte werden lokal gespeichert. Dadurch müssen
    identische Punkte bei späteren Programmaufrufen nicht erneut vom
    Server ausgewertet werden.
    """

    def __init__(
        self,
        api_url: str = API_URL,
        cache_file: Path = CACHE_FILE,
        timeout: float = 30.0,
        retries: int = 5,
        pause: float = 0.05,
    ) -> None:
        self.api_url = api_url
        self.cache_file = Path(cache_file)
        self.timeout = timeout
        self.retries = retries
        self.pause = pause

        self.cache_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.cache = self._load_cache()
        self.session = requests.Session()

    def _load_cache(self) -> dict[str, float]:
        """
        Lädt bereits gespeicherte Auswertungen.
        """
        if not self.cache_file.exists():
            return {}

        try:
            with self.cache_file.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            return {str(key): float(value) for key, value in data.items()}

        except (json.JSONDecodeError, OSError, ValueError):
            print(
                "Warnung: Der vorhandene API-Cache konnte nicht "
                "gelesen werden. Es wird ein neuer Cache verwendet."
            )
            return {}

    def _save_cache(self) -> None:
        """
        Speichert den Cache zunächst temporär und ersetzt anschließend
        die bisherige Datei. Dadurch wird das Risiko einer beschädigten
        Cache-Datei verringert.
        """
        temporary_file = self.cache_file.with_suffix(".json.tmp")

        with temporary_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                self.cache,
                file,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )

        temporary_file.replace(self.cache_file)

    @staticmethod
    def _validate_coordinates(
        x: float,
        y: float,
    ) -> tuple[float, float]:
        """
        Prüft, ob ein Punkt innerhalb des zulässigen Gebiets liegt.
        """
        x = float(x)
        y = float(y)

        if not (LOWER_BOUND <= x <= UPPER_BOUND and LOWER_BOUND <= y <= UPPER_BOUND):
            raise ValueError(
                "Der Punkt muss innerhalb von [-5, 5]^2 liegen. "
                f"Übergeben wurde ({x}, {y})."
            )

        return x, y

    @staticmethod
    def _cache_key(
        x: float,
        y: float,
    ) -> str:
        """
        Erzeugt einen reproduzierbaren Schlüssel für den Cache.
        """
        return f"{x:.8f},{y:.8f}"

    @staticmethod
    def _extract_result(response_data: dict) -> float:
        """
        Liest den Höhenwert aus der JSON-Antwort.

        Mehrere mögliche Feldnamen werden berücksichtigt, damit die
        Implementierung gegenüber kleinen Änderungen der API robust ist.
        """
        for field in (
            "result",
            "height",
            "value",
            "z",
        ):
            if field in response_data:
                return float(response_data[field])

        numeric_values = [
            value for value in response_data.values() if isinstance(value, (int, float))
        ]

        if len(numeric_values) == 1:
            return float(numeric_values[0])

        raise ValueError(
            "Die Serverantwort enthält keinen eindeutig "
            f"erkennbaren Höhenwert: {response_data}"
        )

    def evaluate(
        self,
        x: float,
        y: float,
    ) -> float:
        """
        Gibt die Höhe am Punkt (x, y) zurück.

        Liegt der Punkt bereits im Cache, wird keine neue HTTP-Anfrage
        gesendet.
        """
        x, y = self._validate_coordinates(x, y)
        key = self._cache_key(x, y)

        if key in self.cache:
            return self.cache[key]

        last_error: Exception | None = None

        for attempt in range(1, self.retries + 1):
            try:
                response = self.session.get(
                    self.api_url,
                    params={
                        "x": x,
                        "y": y,
                    },
                    timeout=self.timeout,
                )

                response.raise_for_status()

                result = self._extract_result(response.json())

                self.cache[key] = result
                self._save_cache()

                time.sleep(self.pause)

                return result

            except (
                requests.RequestException,
                ValueError,
                TypeError,
            ) as error:
                last_error = error

                if attempt < self.retries:
                    wait_time = 2 * attempt

                    print(
                        f"Versuch {attempt}/{self.retries} für "
                        f"({x:.4f}, {y:.4f}) fehlgeschlagen. "
                        f"Neuer Versuch in {wait_time} Sekunden."
                    )

                    time.sleep(wait_time)

        raise RuntimeError(
            f"Die Blackbox konnte am Punkt ({x}, {y}) nicht ausgewertet werden."
        ) from last_error

    def cached_points(self) -> int:
        """
        Anzahl der lokal gespeicherten Auswertungen.
        """
        return len(self.cache)

    def close(self) -> None:
        """
        Schließt die HTTP-Sitzung.
        """
        self.session.close()
