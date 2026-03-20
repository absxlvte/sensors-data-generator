from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset, ProcessedCurve, ProcessedView


def _moving_average(signal: np.ndarray, window_size: int) -> np.ndarray:
    if signal.size == 0 or window_size <= 1:
        return signal.copy()
    padded = np.pad(signal, (window_size // 2, window_size // 2), mode="edge")
    kernel = np.ones(window_size, dtype=float) / window_size
    return np.convolve(padded, kernel, mode="valid")


def build_processed_view(dataset: GeneratedDataset) -> ProcessedView:
    time_axis = np.asarray(dataset.meta.get("time_axis", []), dtype=float)
    ideal_level = np.asarray(dataset.meta.get("ideal_level", []), dtype=float)
    detected_level = np.asarray(dataset.meta.get("detected_level", []), dtype=float)
    filtered_level = _moving_average(detected_level, 5)

    return ProcessedView(
        title="Обработка уровня жидкости",
        curves=[
            ProcessedCurve(
                name="Эталонный уровень",
                x=time_axis,
                y=ideal_level,
            ),
            ProcessedCurve(
                name="Определённый уровень",
                x=time_axis,
                y=filtered_level,
            ),
        ],
    )
