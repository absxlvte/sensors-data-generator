from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset, ProcessedCurve, ProcessedView


def _median_filter(signal: np.ndarray, window_size: int) -> np.ndarray:
    if signal.size == 0 or window_size <= 1:
        return signal.copy()
    radius = window_size // 2
    padded = np.pad(signal, (radius, radius), mode="edge")
    filtered = np.empty_like(signal, dtype=float)
    for index in range(signal.size):
        filtered[index] = np.median(padded[index : index + window_size])
    return filtered


def _moving_average(signal: np.ndarray, window_size: int) -> np.ndarray:
    if signal.size == 0 or window_size <= 1:
        return signal.copy()
    padded = np.pad(signal, (window_size // 2, window_size // 2), mode="edge")
    kernel = np.ones(window_size, dtype=float) / window_size
    return np.convolve(padded, kernel, mode="valid")


def _restore_current(dataset: GeneratedDataset) -> np.ndarray:
    adc_signal = np.asarray(dataset.meta.get("adc_signal", []), dtype=float)
    adc_bits = int(dataset.meta.get("adc_bits", 12))
    detector_gain = float(dataset.meta.get("detector_gain", 0.5))
    v_ref = float(dataset.meta.get("v_ref", 5.0))
    denominator = (2**adc_bits) * detector_gain
    if adc_signal.size == 0 or denominator == 0:
        return np.asarray([], dtype=float)
    voltage = adc_signal * v_ref / (2**adc_bits)
    current = voltage / detector_gain
    return current


def _filter_current(signal: np.ndarray) -> np.ndarray:
    filtered = _median_filter(signal, window_size=7)
    filtered = _moving_average(filtered, window_size=9)
    return filtered


def build_processed_view(dataset: GeneratedDataset) -> ProcessedView:
    time_axis = np.asarray(dataset.meta.get("time_axis", []), dtype=float)
    restored_current = _restore_current(dataset)
    filtered_current = _filter_current(restored_current)
    base_current = float(dataset.meta.get("base_current", 0.0))
    base_line = np.full_like(time_axis, base_current, dtype=float)

    return ProcessedView(
        title="Обработка датчика крови",
        curves=[
            ProcessedCurve(
                name="Восстановленный ток",
                x=time_axis,
                y=filtered_current,
            ),
            ProcessedCurve(
                name="Базовый ток",
                x=time_axis,
                y=base_line,
            ),
        ],
    )
