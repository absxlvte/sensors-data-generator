from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import DataSeries, GeneratedDataset
from generator_app.core.models.edit_model import EditModel
from generator_app.plotting.pchip_adapter import build_curve_from_control_points


def _build_random_state(point_count: int, outlier_count: int) -> dict[str, np.ndarray]:
    safe_outlier_count = max(0, min(outlier_count, point_count))
    if safe_outlier_count == 0:
        outlier_indices = np.array([], dtype=int)
        outlier_directions = np.array([], dtype=float)
    else:
        outlier_indices = np.random.choice(point_count, safe_outlier_count, replace=False)
        outlier_directions = np.random.choice(np.array([-1.0, 1.0]), safe_outlier_count)

    return {
        "outlier_indices": outlier_indices,
        "outlier_directions": outlier_directions,
        "noise_profile": np.random.normal(size=point_count),
    }


def _build_linear_mapping(
    source_min: float,
    source_max: float,
    target_min: float,
    target_max: float,
) -> tuple[float, float]:
    if np.isclose(source_max, source_min):
        return 0.0, (target_min + target_max) / 2.0
    scale = (target_max - target_min) / (source_max - source_min)
    offset = target_min - source_min * scale
    return float(scale), float(offset)


def _apply_linear_mapping(values: np.ndarray, scale: float, offset: float) -> np.ndarray:
    return np.asarray(values, dtype=float) * scale + offset


def _scale_signal(values: np.ndarray, target_min: float, target_max: float) -> np.ndarray:
    current_min = float(np.min(values))
    current_max = float(np.max(values))
    if np.isclose(current_min, current_max):
        return np.full_like(values, (target_min + target_max) / 2.0, dtype=float)
    return target_min + (values - current_min) * (target_max - target_min) / (current_max - current_min)


def _apply_outliers(
    signal: np.ndarray,
    outlier_indices: np.ndarray,
    outlier_directions: np.ndarray,
    strength: float,
) -> np.ndarray:
    result = np.asarray(signal, dtype=float).copy()
    if outlier_indices.size == 0:
        return result
    outlier_values = strength * float(np.max(np.abs(result))) * outlier_directions
    result[outlier_indices] += outlier_values
    return result


def _apply_noise(signal: np.ndarray, noise_profile: np.ndarray, noise_level: float) -> np.ndarray:
    if noise_level <= 0:
        return np.asarray(signal, dtype=float).copy()
    amplitude = float(np.max(np.abs(signal)))
    return np.asarray(signal, dtype=float) + noise_level * amplitude * noise_profile


def _build_conductivity_arrays(
    params: dict[str, int | float | list[tuple[float, float]]],
    random_state: dict[str, np.ndarray],
) -> dict[str, object]:
    point_count = int(params["point_count"])
    adc_bits = int(params["adc_bits"])
    z_min = 0.0
    z_max = float((2**adc_bits) - 1)
    time_start = float(params["time_start"])
    time_stop = float(params["time_stop"])
    outlier_strength = float(params["outlier_strength"])
    noise_level = float(params["noise_level"])
    control_points = sorted((float(x_value), float(y_value)) for x_value, y_value in params["control_points"])

    control_array = np.asarray(control_points, dtype=float)
    control_time = control_array[:, 0]
    control_value = control_array[:, 1]
    time_axis = np.linspace(time_start, time_stop, point_count, dtype=float)

    baseline = build_curve_from_control_points(control_time, control_value, time_axis)
    signal_with_outliers = _apply_outliers(
        baseline,
        random_state["outlier_indices"],
        random_state["outlier_directions"],
        outlier_strength,
    )
    noisy_signal = _apply_noise(signal_with_outliers, random_state["noise_profile"], noise_level)

    raw_signal_min = float(np.min(noisy_signal))
    raw_signal_max = float(np.max(noisy_signal))
    adc_scale, adc_offset = _build_linear_mapping(raw_signal_min, raw_signal_max, z_min, z_max)
    adc_signal = _apply_linear_mapping(noisy_signal, adc_scale, adc_offset)
    adc_signal = _scale_signal(adc_signal, z_max * 0.1, z_max * 0.9)
    adc_signal = np.clip(adc_signal, z_min, z_max).astype(int)

    control_min = float(np.min(control_value))
    control_max = float(np.max(control_value))
    control_scale, control_offset = _build_linear_mapping(control_min, control_max, z_min, z_max)
    control_display = _apply_linear_mapping(control_value, control_scale, control_offset)
    control_display = _scale_signal(control_display, z_max * 0.1, z_max * 0.9)
    control_display = np.clip(control_display, z_min, z_max)
    reference_signal = build_curve_from_control_points(control_time, control_display, time_axis)

    return {
        "time_axis": time_axis,
        "baseline": baseline,
        "noisy_signal": noisy_signal,
        "adc_signal": adc_signal,
        "reference_signal": reference_signal,
        "control_time": control_time,
        "control_value": control_value,
        "control_display": control_display,
        "control_points": control_points,
        "display_range": (z_max * 0.1, z_max * 0.9),
        "adc_mapping": {
            "raw_min": raw_signal_min,
            "raw_max": raw_signal_max,
            "display_min": z_max * 0.1,
            "display_max": z_max * 0.9,
        },
        "control_mapping": {
            "raw_min": control_min,
            "raw_max": control_max,
            "display_min": z_max * 0.1,
            "display_max": z_max * 0.9,
        },
    }


def generate_conductivity_dataset(
    params: dict[str, int | float | list[tuple[float, float]]],
    random_state: dict[str, np.ndarray] | None = None,
) -> GeneratedDataset:
    point_count = int(params["point_count"])
    current_random_state = random_state or _build_random_state(point_count, int(params["outlier_count"]))
    arrays = _build_conductivity_arrays(params, current_random_state)
    adc_bits = int(params["adc_bits"])
    z_max = float((2**adc_bits) - 1)

    return GeneratedDataset(
        task_id="conductivity_sensor",
        series=[
            DataSeries(
                id="conductivity_output",
                name="Выход АЦП",
                x=np.asarray(arrays["time_axis"], dtype=float),
                y=np.asarray(arrays["adc_signal"], dtype=float),
                editable=False,
            ),
            DataSeries(
                id="conductivity_reference",
                name="Опорная кривая",
                x=np.asarray(arrays["time_axis"], dtype=float),
                y=np.asarray(arrays["reference_signal"], dtype=float),
                editable=False,
            ),
            DataSeries(
                id="conductivity_nodes",
                name="Опорные точки",
                x=np.asarray(arrays["control_time"], dtype=float),
                y=np.asarray(arrays["control_display"], dtype=float),
                editable=True,
            ),
        ],
        edit_model=EditModel(editable_series_ids=["conductivity_nodes"]),
        meta={
            "time_axis": arrays["time_axis"],
            "baseline": arrays["baseline"],
            "noisy_signal": arrays["noisy_signal"],
            "adc_signal": arrays["adc_signal"],
            "reference_signal": arrays["reference_signal"],
            "control_points": list(arrays["control_points"]),
            "control_display_points": list(
                zip(arrays["control_time"].tolist(), arrays["control_display"].tolist(), strict=True)
            ),
            "adc_mapping": arrays["adc_mapping"],
            "control_mapping": arrays["control_mapping"],
            "random_state": current_random_state,
            "z_range": (0.0, z_max),
            "adc_bits": adc_bits,
            "drag_config": {
                "conductivity_nodes": {
                    "x_locked": False,
                    "x_min": float(params["time_start"]),
                    "x_max": float(params["time_stop"]),
                    "y_min": float(arrays["display_range"][0]),
                    "y_max": float(arrays["display_range"][1]),
                    "round_y": True,
                }
            },
        },
    )
