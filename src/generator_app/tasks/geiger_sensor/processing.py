from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset, ProcessedCurve, ProcessedView


def _estimate_frequency(binary_signal: np.ndarray, sampling_rate: int, window_seconds: float = 1.0) -> np.ndarray:
    if binary_signal.size == 0:
        return binary_signal.copy()
    window_size = max(1, int(window_seconds * sampling_rate))
    kernel = np.ones(window_size, dtype=float)
    estimated_counts = np.convolve(binary_signal, kernel, mode="same")
    return estimated_counts / window_seconds


def _moving_average(signal: np.ndarray, window_size: int) -> np.ndarray:
    if signal.size == 0 or window_size <= 1:
        return signal.copy()
    if window_size % 2 == 0:
        window_size += 1
    padded = np.pad(signal, (window_size // 2, window_size // 2), mode="edge")
    kernel = np.ones(window_size, dtype=float) / window_size
    return np.convolve(padded, kernel, mode="valid")


def build_processed_view(dataset: GeneratedDataset) -> ProcessedView:
    time_axis = np.asarray(dataset.meta.get("time_axis", []), dtype=float)
    binary_signal = np.asarray(dataset.meta.get("binary_signal", []), dtype=float)
    target_frequency = np.asarray(dataset.meta.get("target_frequency", []), dtype=float)
    sampling_rate = int(dataset.meta.get("sampling_rate", 1000))

    estimated_frequency = _estimate_frequency(binary_signal, sampling_rate)
    estimated_frequency = _moving_average(estimated_frequency, max(3, sampling_rate // 10))

    return ProcessedView(
        title="Обработка данных счётчика Гейгера",
        curves=[
            ProcessedCurve(
                name="Заданная частота",
                x=time_axis,
                y=target_frequency,
            ),
            ProcessedCurve(
                name="Оценённая частота",
                x=time_axis,
                y=estimated_frequency,
            ),
        ],
    )
