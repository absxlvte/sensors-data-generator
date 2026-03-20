from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset, ProcessedCurve, ProcessedView
from generator_app.tasks.ph_sensor.generator import _voltage_to_ph, _z_to_voltage_bipolar


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


def _restore_ph(dataset: GeneratedDataset) -> np.ndarray:
    adc_signal = np.asarray(dataset.meta.get("adc_signal", []), dtype=float)
    voltage = _z_to_voltage_bipolar(
        adc_signal,
        int(dataset.meta.get("adc_bits", 12)),
        float(dataset.meta.get("v_ref", 5.0)),
    )
    return _voltage_to_ph(
        voltage,
        float(dataset.meta.get("temperature_k", 298.0)),
        float(dataset.meta.get("gas_const", 8.314)),
        float(dataset.meta.get("faraday_const", 96485.0)),
    )


def build_processed_view(dataset: GeneratedDataset) -> ProcessedView:
    time_axis = np.asarray(dataset.meta.get("time_axis", []), dtype=float)
    baseline_ph = np.asarray(dataset.meta.get("baseline_ph", []), dtype=float)
    restored_ph = _restore_ph(dataset)
    filtered_ph = _moving_average(_median_filter(restored_ph, 7), 9)

    return ProcessedView(
        title="Обработка pH",
        curves=[
            ProcessedCurve(
                name="Эталонный pH",
                x=time_axis,
                y=baseline_ph,
            ),
            ProcessedCurve(
                name="После фильтрации",
                x=time_axis,
                y=filtered_ph,
            ),
        ],
    )
