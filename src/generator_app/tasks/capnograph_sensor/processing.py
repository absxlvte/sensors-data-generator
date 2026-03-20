from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset, ProcessedCurve, ProcessedView


def _moving_average(signal: np.ndarray, window_size: int) -> np.ndarray:
    if signal.size == 0 or window_size <= 1:
        return signal.copy()
    if window_size % 2 == 0:
        window_size += 1
    padded = np.pad(signal, (window_size // 2, window_size // 2), mode="edge")
    kernel = np.ones(window_size, dtype=float) / window_size
    return np.convolve(padded, kernel, mode="valid")


def _median_filter(signal: np.ndarray, window_size: int) -> np.ndarray:
    if signal.size == 0 or window_size <= 1:
        return signal.copy()
    if window_size % 2 == 0:
        window_size += 1
    radius = window_size // 2
    padded = np.pad(signal, (radius, radius), mode="edge")
    filtered = np.empty_like(signal, dtype=float)
    for index in range(signal.size):
        filtered[index] = np.median(padded[index : index + window_size])
    return filtered


def _restore_signal(dataset: GeneratedDataset) -> np.ndarray:
    adc_signal = np.asarray(dataset.meta.get("adc_signal", []), dtype=float)
    mapping = dataset.meta.get("adc_mapping", {})
    display_min = float(mapping.get("display_min", 0.0))
    display_max = float(mapping.get("display_max", 1.0))
    raw_min = float(mapping.get("raw_min", 0.0))
    raw_max = float(mapping.get("raw_max", 1.0))
    if adc_signal.size == 0:
        return adc_signal
    if np.isclose(display_max, display_min):
        return np.full_like(adc_signal, raw_min)
    return raw_min + (adc_signal - display_min) * (raw_max - raw_min) / (display_max - display_min)


def _filter_signal(signal: np.ndarray) -> np.ndarray:
    filtered = _median_filter(signal, window_size=7)
    filtered = _moving_average(filtered, window_size=9)
    return filtered


def build_processed_view(dataset: GeneratedDataset) -> ProcessedView:
    time_axis = np.asarray(dataset.meta.get("time_axis", []), dtype=float)
    baseline = np.asarray(dataset.meta.get("baseline", []), dtype=float)
    restored = _restore_signal(dataset)
    filtered = _filter_signal(restored)

    return ProcessedView(
        title="Обработка капнограммы",
        curves=[
            ProcessedCurve(
                name="Эталонная капнограмма",
                x=time_axis,
                y=baseline,
                color="#00897B",
                line_style="solid",
            ),
            ProcessedCurve(
                name="После фильтрации",
                x=time_axis,
                y=filtered,
                color="#E65100",
                line_style="dash",
            ),
        ],
    )
