from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import DataSeries, GeneratedDataset
from generator_app.core.models.edit_model import EditModel
from generator_app.plotting.pchip_adapter import build_curve_from_control_points


def _current_to_z(current: float, adc_bits: int, detector_gain: float, v_ref: float) -> float:
    return (2**adc_bits) * detector_gain * current / v_ref


def _z_to_current(z_value: np.ndarray | float, adc_bits: int, detector_gain: float, v_ref: float) -> np.ndarray:
    return np.asarray(z_value, dtype=float) * v_ref / ((2**adc_bits) * detector_gain)


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


def _build_affine_mapping(
    source_min: float,
    source_max: float,
    target_center: float,
    half_span: float,
) -> tuple[float, float]:
    if np.isclose(source_max, source_min):
        return 0.0, target_center
    scale = (2.0 * half_span) / (source_max - source_min)
    offset = target_center - half_span - source_min * scale
    return float(scale), float(offset)


def _apply_mapping(values: np.ndarray, scale: float, offset: float) -> np.ndarray:
    return np.asarray(values, dtype=float) * scale + offset


def _build_blood_arrays(
    params: dict[str, int | float | list[tuple[float, float]]],
    random_state: dict[str, np.ndarray],
) -> dict[str, object]:
    base_current = float(params["base_current"])
    point_count = int(params["point_count"])
    v_ref = float(params["v_ref"])
    adc_bits = int(params["adc_bits"])
    detector_gain = float(params["detector_gain"])
    shift = float(params["shift"])
    outlier_strength = float(params["outlier_strength"])
    noise_level = float(params["noise_level"])
    time_start = float(params["time_start"])
    time_stop = float(params["time_stop"])
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

    center_z = _current_to_z(base_current, adc_bits, detector_gain, v_ref)
    min_z = max(0.0, center_z - shift)
    max_z = min(float((2**adc_bits) - 1), center_z + shift)
    half_span = min(center_z - min_z, max_z - center_z)

    raw_min = float(np.min(noisy_signal))
    raw_max = float(np.max(noisy_signal))
    adc_scale, adc_offset = _build_affine_mapping(raw_min, raw_max, center_z, half_span)

    adc_signal = _apply_mapping(noisy_signal, adc_scale, adc_offset)
    adc_signal = np.clip(adc_signal, 0.0, float((2**adc_bits) - 1)).astype(int)

    control_display = _apply_mapping(control_value, adc_scale, adc_offset)
    control_display = np.clip(control_display, 0.0, float((2**adc_bits) - 1))
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
        "adc_mapping": {
            "scale": adc_scale,
            "offset": adc_offset,
            "raw_min": raw_min,
            "raw_max": raw_max,
            "center_z": center_z,
            "half_span": half_span,
            "min_z": min_z,
            "max_z": max_z,
        },
    }


def generate_blood_dataset(
    params: dict[str, int | float | list[tuple[float, float]]],
    random_state: dict[str, np.ndarray] | None = None,
) -> GeneratedDataset:
    point_count = int(params["point_count"])
    current_random_state = random_state or _build_random_state(point_count, int(params["outlier_count"]))
    arrays = _build_blood_arrays(params, current_random_state)
    adc_bits = int(params["adc_bits"])

    return GeneratedDataset(
        task_id="blood_sensor",
        series=[
            DataSeries(
                id="blood_output",
                name="Выход АЦП",
                x=np.asarray(arrays["time_axis"], dtype=float),
                y=np.asarray(arrays["adc_signal"], dtype=float),
                editable=False,
            ),
            DataSeries(
                id="blood_reference",
                name="Опорная кривая",
                x=np.asarray(arrays["time_axis"], dtype=float),
                y=np.asarray(arrays["reference_signal"], dtype=float),
                editable=False,
            ),
            DataSeries(
                id="blood_nodes",
                name="Опорные точки",
                x=np.asarray(arrays["control_time"], dtype=float),
                y=np.asarray(arrays["control_display"], dtype=float),
                editable=True,
            ),
        ],
        edit_model=EditModel(editable_series_ids=["blood_nodes"]),
        meta={
            "time_axis": arrays["time_axis"],
            "baseline": arrays["baseline"],
            "adc_signal": arrays["adc_signal"],
            "noisy_signal": arrays["noisy_signal"],
            "reference_signal": arrays["reference_signal"],
            "control_points": list(arrays["control_points"]),
            "control_display_points": list(
                zip(arrays["control_time"].tolist(), arrays["control_display"].tolist(), strict=True)
            ),
            "adc_mapping": arrays["adc_mapping"],
            "adc_bits": adc_bits,
            "v_ref": float(params["v_ref"]),
            "detector_gain": float(params["detector_gain"]),
            "base_current": float(params["base_current"]),
            "random_state": current_random_state,
            "drag_config": {
                "blood_nodes": {
                    "x_locked": False,
                    "x_min": float(params["time_start"]),
                    "x_max": float(params["time_stop"]),
                    "y_min": float(arrays["adc_mapping"]["min_z"]),
                    "y_max": float(arrays["adc_mapping"]["max_z"]),
                    "round_y": True,
                }
            },
        },
    )
