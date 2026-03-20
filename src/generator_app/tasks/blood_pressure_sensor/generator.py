from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import DataSeries, GeneratedDataset
from generator_app.core.models.edit_model import EditModel


def _voltage_to_z(voltage: np.ndarray | float, adc_bits: int, v_ref: float) -> np.ndarray:
    return (2**adc_bits) * np.asarray(voltage, dtype=float) / v_ref


def _z_to_voltage(z_value: np.ndarray | float, adc_bits: int, v_ref: float) -> np.ndarray:
    return np.asarray(z_value, dtype=float) * v_ref / (2**adc_bits)


def _moving_average(signal: np.ndarray, window_size: int) -> np.ndarray:
    if signal.size == 0 or window_size <= 1:
        return signal.copy()
    if window_size % 2 == 0:
        window_size += 1
    padded = np.pad(signal, (window_size // 2, window_size // 2), mode="edge")
    kernel = np.ones(window_size, dtype=float) / window_size
    return np.convolve(padded, kernel, mode="valid")


def _estimate_pressures(
    pressure_signal: np.ndarray,
    k1: float,
    k2: float,
) -> tuple[float, float]:
    if pressure_signal.size == 0:
        return 0.0, 0.0

    baseline = _moving_average(pressure_signal, 501)
    pulsation = np.abs(pressure_signal - baseline)
    envelope = _moving_average(pulsation, 301)
    if envelope.size == 0 or float(np.max(envelope)) <= 0:
        return 0.0, 0.0

    threshold = float(np.max(envelope)) * 0.35
    active_indices = np.flatnonzero(envelope >= threshold)
    if active_indices.size == 0:
        return 0.0, 0.0

    systolic_voltage = float(baseline[active_indices[0]])
    diastolic_voltage = float(baseline[active_indices[-1]])
    return systolic_voltage * k1, diastolic_voltage * k2


def generate_blood_pressure_dataset(params: dict[str, int | float]) -> GeneratedDataset:
    duration = float(params["duration"])
    sampling_rate = int(params["sampling_rate"])
    sbp = float(params["sbp"])
    dbp = float(params["dbp"])
    v_ref = float(params["v_ref"])
    adc_bits = int(params["adc_bits"])
    k1 = float(params["k1"])
    k2 = float(params["k2"])

    start_pressure = dbp / k2
    end_pressure = sbp / k1
    initial_pressure = 5.8
    final_pressure = 0.2
    pulse_frequency = 1.8
    pulse_amplitude = 0.5

    num_points = max(3, int(duration * sampling_rate))
    time_axis = np.linspace(0.0, duration, num_points, dtype=float)
    pressure_drop = np.linspace(initial_pressure, final_pressure, num_points, dtype=float)

    within_band = (pressure_drop >= start_pressure) & (pressure_drop <= end_pressure)
    pressure_drop[within_band] += pulse_amplitude * np.sin(2 * np.pi * pulse_frequency * time_axis[within_band])
    pressure_drop += np.random.normal(0.0, 0.02, pressure_drop.shape)

    q1 = float(np.percentile(pressure_drop, 25))
    q3 = float(np.percentile(pressure_drop, 75))
    iqr = q3 - q1
    filter_mask = (pressure_drop >= (q1 - 1.5 * iqr)) & (pressure_drop <= (q3 + 1.5 * iqr))
    filtered_pressure = pressure_drop[filter_mask]
    filtered_time = time_axis[filter_mask]

    adc_signal = np.clip(_voltage_to_z(filtered_pressure, adc_bits, v_ref), 0.0, float((2**adc_bits) - 1)).astype(int)
    estimated_sbp, estimated_dbp = _estimate_pressures(filtered_pressure, k1, k2)

    return GeneratedDataset(
        task_id="blood_pressure_sensor",
        series=[
            DataSeries(
                id="blood_pressure_output",
                name="Выход АЦП",
                x=filtered_time,
                y=adc_signal.astype(float),
                editable=False,
            )
        ],
        edit_model=EditModel(editable_series_ids=[]),
        meta={
            "time_axis": filtered_time,
            "pressure_drop": filtered_pressure,
            "adc_signal": adc_signal,
            "adc_bits": adc_bits,
            "v_ref": v_ref,
            "target_sbp": sbp,
            "target_dbp": dbp,
            "estimated_sbp": estimated_sbp,
            "estimated_dbp": estimated_dbp,
        },
    )
