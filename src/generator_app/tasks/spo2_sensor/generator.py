from __future__ import annotations

import math

import numpy as np

from generator_app.core.models.dataset import DataSeries, GeneratedDataset
from generator_app.core.models.edit_model import EditModel
from generator_app.plotting.pchip_adapter import build_curve_from_control_points


def _voltage_to_z(values: np.ndarray, adc_bits: int, v_ref: float) -> np.ndarray:
    return (2**adc_bits) * np.asarray(values, dtype=float) / v_ref


def _z_to_voltage(values: np.ndarray, adc_bits: int, v_ref: float) -> np.ndarray:
    return np.asarray(values, dtype=float) * v_ref / (2**adc_bits)


def _create_pulse_wave(
    amplitude: float,
    zero_offset: float,
    points: int,
    inverse: bool = False,
    t_start: float = 0.0,
    t_stop: float = 5.0,
) -> tuple[np.ndarray, np.ndarray]:
    t_ref = np.array([0.0, 0.2, 0.5, 0.7, 1.0, 1.5, 1.7], dtype=float)
    v_ref = np.array([0.0, 0.0, 1.0, 0.7, 0.75, 0.0, 0.0], dtype=float)
    v_ref = v_ref - 0.5
    period = 1.5
    periods = math.ceil((t_stop - t_start) / period)

    control_time = []
    control_value = []
    for period_index in range(periods + 1):
        shifted_time = t_ref + period_index * period
        mask = shifted_time <= t_stop
        control_time.extend(shifted_time[mask].tolist())
        control_value.extend(v_ref[mask].tolist())

    control_time = np.asarray(control_time, dtype=float)
    control_value = np.asarray(control_value, dtype=float)
    unique_time, unique_indices = np.unique(control_time, return_index=True)
    unique_value = control_value[unique_indices]
    time_axis = np.linspace(t_start, max(t_stop, unique_time[-1]), points, dtype=float)
    wave = build_curve_from_control_points(unique_time, unique_value, time_axis)
    if inverse:
        wave = -wave
    return time_axis, wave * 2.0 * amplitude + zero_offset


def _compute_spo2(z660: np.ndarray, z940: np.ndarray, adc_bits: int, v_ref: float, coef_a: float, coef_b: float) -> dict[str, float]:
    centered_940 = z940 - np.mean(z940)
    centered_660 = z660 - np.mean(z660)
    ac_from_940 = (np.max(centered_940) - np.min(centered_940)) / 2.0
    ac_from_660 = (np.max(centered_660) - np.min(centered_660)) / 2.0
    mean_660 = float(np.mean(z660))
    mean_940 = float(np.mean(z940))
    ratio = (ac_from_660 / mean_660) / (ac_from_940 / mean_940)
    estimated_spo2 = coef_a - coef_b * ratio

    return {
        "ratio": float(ratio),
        "estimated_spo2": float(estimated_spo2),
        "ac_660_voltage": float(_z_to_voltage(ac_from_660, adc_bits, v_ref)),
        "ac_940_voltage": float(_z_to_voltage(ac_from_940, adc_bits, v_ref)),
        "dc_660_voltage": float(_z_to_voltage(mean_660, adc_bits, v_ref)),
        "dc_940_voltage": float(_z_to_voltage(mean_940, adc_bits, v_ref)),
    }


def generate_spo2_dataset(params: dict[str, int | float]) -> GeneratedDataset:
    target_spo2 = float(params["spo2"])
    point_count = int(params["point_count"])
    adc_bits = int(params["adc_bits"])
    v_ref = float(params["v_ref"])
    coef_a = float(params["coef_a"])
    coef_b = float(params["coef_b"])

    dc660 = 1.3
    dc940 = 1.5
    ac660 = 0.6
    ac940 = (ac660 * coef_b * dc940) / (dc660 * (coef_a - target_spo2))

    time_axis, voltage_660 = _create_pulse_wave(
        amplitude=ac660,
        zero_offset=dc660,
        points=point_count,
        inverse=True,
    )
    _, voltage_940 = _create_pulse_wave(
        amplitude=ac940,
        zero_offset=dc940,
        points=point_count,
        inverse=False,
    )

    z660 = _voltage_to_z(voltage_660, adc_bits, v_ref)
    z940 = _voltage_to_z(voltage_940, adc_bits, v_ref)
    max_code = float((2**adc_bits) - 1)
    z660 = np.clip(z660, 0.0, max_code)
    z940 = np.clip(z940, 0.0, max_code)

    metrics = _compute_spo2(z660, z940, adc_bits, v_ref, coef_a, coef_b)

    return GeneratedDataset(
        task_id="spo2_sensor",
        series=[
            DataSeries(
                id="spo2_660",
                name="Z660",
                x=time_axis,
                y=z660,
                editable=False,
            ),
            DataSeries(
                id="spo2_940",
                name="Z940",
                x=time_axis,
                y=z940,
                editable=False,
            ),
        ],
        edit_model=EditModel(editable_series_ids=[]),
        meta={
            "time_axis": time_axis,
            "z660": z660,
            "z940": z940,
            "target_spo2": target_spo2,
            "estimated_spo2": metrics["estimated_spo2"],
            "ratio": metrics["ratio"],
            "ac_660_voltage": metrics["ac_660_voltage"],
            "ac_940_voltage": metrics["ac_940_voltage"],
            "dc_660_voltage": metrics["dc_660_voltage"],
            "dc_940_voltage": metrics["dc_940_voltage"],
            "adc_bits": adc_bits,
            "v_ref": v_ref,
            "coef_a": coef_a,
            "coef_b": coef_b,
        },
    )
