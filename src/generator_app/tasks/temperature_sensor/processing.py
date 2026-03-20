from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset, ProcessedCurve, ProcessedView


def _moving_average(signal: np.ndarray, window_size: int) -> np.ndarray:
    if signal.size == 0 or window_size <= 1:
        return signal.copy()
    padded = np.pad(signal, (window_size // 2, window_size // 2), mode="edge")
    kernel = np.ones(window_size, dtype=float) / window_size
    return np.convolve(padded, kernel, mode="valid")


def _median_filter(signal: np.ndarray, window_size: int) -> np.ndarray:
    if signal.size == 0 or window_size <= 1:
        return signal.copy()
    radius = window_size // 2
    padded = np.pad(signal, (radius, radius), mode="edge")
    filtered = np.empty_like(signal, dtype=float)
    for index in range(signal.size):
        filtered[index] = np.median(padded[index : index + window_size])
    return filtered


def _restore_temperature(dataset: GeneratedDataset) -> np.ndarray:
    adc_mapping = dataset.meta.get("adc_mapping", {})
    adc_signal = np.asarray(dataset.meta.get("adc_signal", []), dtype=float)
    scale = float(adc_mapping.get("scale", 0.0))
    offset = float(adc_mapping.get("offset", 0.0))
    if adc_signal.size == 0:
        return adc_signal
    if scale == 0.0:
        return np.full_like(adc_signal, float(adc_mapping.get("raw_min", 0.0)))
    return (adc_signal - offset) / scale


def _filter_temperature(signal: np.ndarray) -> np.ndarray:
    filtered = _median_filter(signal, window_size=7)
    filtered = _moving_average(filtered, window_size=9)
    return filtered


def build_processed_view(dataset: GeneratedDataset) -> ProcessedView:
    time_axis = np.asarray(dataset.meta.get("time_axis", []), dtype=float)
    baseline = np.asarray(dataset.meta.get("baseline", []), dtype=float)
    restored = _restore_temperature(dataset)
    filtered = _filter_temperature(restored)

    return ProcessedView(
        title="Обработка температуры",
        curves=[
            ProcessedCurve(
                name="Эталонная температура",
                x=time_axis,
                y=baseline,
            ),
            ProcessedCurve(
                name="После фильтрации",
                x=time_axis,
                y=filtered,
            ),
        ],
    )
