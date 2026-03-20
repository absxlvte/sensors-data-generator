from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import DataSeries, GeneratedDataset
from generator_app.core.models.edit_model import EditModel
from generator_app.plotting.pchip_adapter import build_curve_from_control_points


def _ph_to_voltage(ph_value: np.ndarray | float, temperature_k: float, gas_const: float, faraday_const: float) -> np.ndarray:
    return -(gas_const * temperature_k * 2.303 * np.asarray(ph_value, dtype=float)) / faraday_const


def _voltage_to_ph(voltage: np.ndarray | float, temperature_k: float, gas_const: float, faraday_const: float) -> np.ndarray:
    return -(faraday_const * np.asarray(voltage, dtype=float)) / (2.303 * gas_const * temperature_k)


def _voltage_to_z_bipolar(voltage: np.ndarray | float, adc_bits: int, v_ref: float) -> np.ndarray:
    voltage = np.asarray(voltage, dtype=float)
    result = np.zeros_like(voltage, dtype=float)
    zero_mask = np.isclose(voltage, 0.0)
    non_zero = ~zero_mask
    if np.any(non_zero):
        sign_bit = np.where(voltage[non_zero] >= 0, 0, 1)
        other = np.round((np.abs(voltage[non_zero]) * 2 ** (adc_bits - 1)) / (v_ref / 2.0) - 1.0)
        other = np.clip(other, 0, 2 ** (adc_bits - 1) - 1)
        result[non_zero] = sign_bit * 2 ** (adc_bits - 1) + other
    return result


def _z_to_voltage_bipolar(z_value: np.ndarray | float, adc_bits: int, v_ref: float) -> np.ndarray:
    z_value = np.asarray(z_value, dtype=int)
    sign_bit = z_value >> (adc_bits - 1)
    other = z_value & (2 ** (adc_bits - 1) - 1)
    return ((-1) ** sign_bit * other * v_ref / 2.0) / (2 ** (adc_bits - 1))


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


def _apply_outliers(signal: np.ndarray, outlier_indices: np.ndarray, outlier_directions: np.ndarray, strength: float) -> np.ndarray:
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


def _build_ph_arrays(
    params: dict[str, int | float | list[tuple[float, float]]],
    random_state: dict[str, np.ndarray],
) -> dict[str, object]:
    point_count = int(params["point_count"])
    duration = float(params["duration"])
    adc_bits = int(params["adc_bits"])
    v_ref = float(params["v_ref"])
    temperature_k = float(params["temperature_k"])
    faraday_const = float(params["faraday_const"])
    gas_const = float(params["gas_const"])
    noise_level = float(params["noise_level"])
    outlier_strength = float(params["outlier_strength"])
    control_points = sorted((float(x_value), float(y_value)) for x_value, y_value in params["control_points"])

    control_array = np.asarray(control_points, dtype=float)
    control_time = control_array[:, 0]
    control_ph = control_array[:, 1]
    time_axis = np.linspace(0.0, duration, point_count, dtype=float)

    baseline_ph = build_curve_from_control_points(control_time, control_ph, time_axis)
    baseline_voltage = _ph_to_voltage(baseline_ph, temperature_k, gas_const, faraday_const)
    baseline_adc = _voltage_to_z_bipolar(baseline_voltage, adc_bits, v_ref)

    noisy_adc = _apply_outliers(
        baseline_adc,
        random_state["outlier_indices"],
        random_state["outlier_directions"],
        outlier_strength,
    )
    noisy_adc = _apply_noise(noisy_adc, random_state["noise_profile"], noise_level)
    noisy_adc = np.clip(noisy_adc, 0.0, float((2**adc_bits) - 1))
    adc_signal = np.round(noisy_adc).astype(int)

    noisy_voltage = _z_to_voltage_bipolar(adc_signal, adc_bits, v_ref)
    noisy_ph = _voltage_to_ph(noisy_voltage, temperature_k, gas_const, faraday_const)

    control_voltage = _ph_to_voltage(control_ph, temperature_k, gas_const, faraday_const)
    control_display = _voltage_to_z_bipolar(control_voltage, adc_bits, v_ref)

    acidic_guide = float(_voltage_to_z_bipolar(_ph_to_voltage(0.1, temperature_k, gas_const, faraday_const), adc_bits, v_ref))
    neutral_guide = float(_voltage_to_z_bipolar(_ph_to_voltage(7.0, temperature_k, gas_const, faraday_const), adc_bits, v_ref))
    alkaline_guide = float(_voltage_to_z_bipolar(_ph_to_voltage(14.0, temperature_k, gas_const, faraday_const), adc_bits, v_ref))
    adc_lower = min(acidic_guide, alkaline_guide)
    adc_upper = max(acidic_guide, alkaline_guide)
    control_display = np.clip(control_display, adc_lower, adc_upper)
    reference_signal = build_curve_from_control_points(control_time, control_display, time_axis)

    return {
        "time_axis": time_axis,
        "baseline_ph": baseline_ph,
        "noisy_ph": noisy_ph,
        "adc_signal": adc_signal,
        "reference_signal": reference_signal,
        "control_time": control_time,
        "control_ph": control_ph,
        "control_display": control_display,
        "control_points": control_points,
        "z_bounds": (adc_lower, adc_upper),
        "ph_guides": {
            "acidic": acidic_guide,
            "neutral": neutral_guide,
            "alkaline": alkaline_guide,
        },
    }


def generate_ph_dataset(
    params: dict[str, int | float | list[tuple[float, float]]],
    random_state: dict[str, np.ndarray] | None = None,
) -> GeneratedDataset:
    point_count = int(params["point_count"])
    adc_bits = int(params["adc_bits"])
    v_ref = float(params["v_ref"])
    temperature_k = float(params["temperature_k"])
    faraday_const = float(params["faraday_const"])
    gas_const = float(params["gas_const"])
    duration = float(params["duration"])
    current_random_state = random_state or _build_random_state(point_count, int(params["outlier_count"]))
    arrays = _build_ph_arrays(params, current_random_state)

    time_axis = np.asarray(arrays["time_axis"], dtype=float)

    return GeneratedDataset(
        task_id="ph_sensor",
        series=[
            DataSeries(
                id="ph_output",
                name="Выход АЦП",
                x=time_axis,
                y=np.asarray(arrays["adc_signal"], dtype=float),
                editable=False,
            ),
            DataSeries(
                id="ph_reference",
                name="Опорная кривая",
                x=time_axis,
                y=np.asarray(arrays["reference_signal"], dtype=float),
                editable=False,
            ),
            DataSeries(
                id="ph_nodes",
                name="Опорные точки",
                x=np.asarray(arrays["control_time"], dtype=float),
                y=np.asarray(arrays["control_display"], dtype=float),
                editable=True,
            ),
            DataSeries(
                id="ph_acidic",
                name="pH = 0.1",
                x=time_axis,
                y=np.full_like(time_axis, float(arrays["ph_guides"]["acidic"])),
                editable=False,
            ),
            DataSeries(
                id="ph_neutral",
                name="pH = 7",
                x=time_axis,
                y=np.full_like(time_axis, float(arrays["ph_guides"]["neutral"])),
                editable=False,
            ),
            DataSeries(
                id="ph_alkaline",
                name="pH = 14",
                x=time_axis,
                y=np.full_like(time_axis, float(arrays["ph_guides"]["alkaline"])),
                editable=False,
            ),
        ],
        edit_model=EditModel(editable_series_ids=["ph_nodes"]),
        meta={
            "time_axis": arrays["time_axis"],
            "baseline_ph": arrays["baseline_ph"],
            "noisy_ph": arrays["noisy_ph"],
            "adc_signal": arrays["adc_signal"],
            "reference_signal": arrays["reference_signal"],
            "control_points": list(arrays["control_points"]),
            "control_display_points": list(
                zip(arrays["control_time"].tolist(), arrays["control_display"].tolist(), strict=True)
            ),
            "adc_bits": adc_bits,
            "v_ref": v_ref,
            "temperature_k": temperature_k,
            "faraday_const": faraday_const,
            "gas_const": gas_const,
            "random_state": current_random_state,
            "drag_config": {
                "ph_nodes": {
                    "x_locked": False,
                    "x_min": 0.0,
                    "x_max": duration,
                    "y_min": float(arrays["z_bounds"][0]),
                    "y_max": float(arrays["z_bounds"][1]),
                    "round_y": True,
                }
            },
        },
    )
