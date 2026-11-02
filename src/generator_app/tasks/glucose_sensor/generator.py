from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import DataSeries, GeneratedDataset
from generator_app.core.models.edit_model import EditModel
from generator_app.plotting.pchip_adapter import build_curve_from_control_points
from generator_app.tasks.glucose_sensor.integration import trapezoidal_integral


GLUCOSE_FREQUENCIES = np.linspace(10, 100, 10, dtype=float)
GLUCOSE_TIME_POINTS = np.array([0, 60, 160, 210, 410, 530, 660, 760, 830, 930, 960, 1060], dtype=float)
GLUCOSE_CONCENTRATION_POINTS = np.array([120, 120, 250, 50, 140, 120, 120, 200, 60, 130, 120, 120], dtype=float)
GLUCOSE_HEIGHTS = list(range(10, 60, 5))
GLUCOSE_QUANTIZATION_HEIGHTS_DESC = list(range(55, 9, -1))


def _build_hyperbola(height: float, noise_scale: float) -> np.ndarray:
    phase_factor = np.cos(np.deg2rad(np.random.randint(-5, 6)))
    values = (700 / (GLUCOSE_FREQUENCIES + 10) + height) * phase_factor
    values = np.round(values + noise_scale * np.random.randn(len(values)))
    return values.astype(float)


def _build_reference_family(noise_scale: float) -> tuple[list[np.ndarray], np.ndarray, float, float]:
    family_curves = [_build_hyperbola(float(height), noise_scale) for height in GLUCOSE_HEIGHTS]
    areas = np.array(
        [trapezoidal_integral(curve, GLUCOSE_FREQUENCIES) for curve in family_curves],
        dtype=float,
    )
    k = (300.0 - 20.0) / (areas[0] - areas[-1])
    b = 300.0 - k * areas[0]
    return family_curves, areas, float(k), float(b)


def _build_quantization_concentration_family_desc(noise_scale: float, k: float, b: float) -> np.ndarray:
    concentrations: list[float] = []
    for height in GLUCOSE_QUANTIZATION_HEIGHTS_DESC:
        curve = _build_hyperbola(float(height), noise_scale)
        area = trapezoidal_integral(curve, GLUCOSE_FREQUENCIES)
        concentrations.append(k * area + b)
    return np.asarray(concentrations, dtype=float)


def _quantize_reference_signal(reference_concentration: np.ndarray, concentration_family_desc: np.ndarray) -> np.ndarray:
    quantized_signal = np.zeros_like(reference_concentration)
    for index in range(len(concentration_family_desc) - 1):
        mask = (reference_concentration >= concentration_family_desc[index]) & (
            reference_concentration < concentration_family_desc[index + 1]
        )
        quantized_signal = np.where(mask, concentration_family_desc[index], quantized_signal)

    final_mask = reference_concentration >= concentration_family_desc[-1]
    quantized_signal = np.where(final_mask, concentration_family_desc[-1], quantized_signal)
    return quantized_signal


def _map_quantized_signal_to_heights(
    quantized_signal: np.ndarray,
    concentration_family_desc: np.ndarray,
) -> list[int]:
    mapped_heights: list[int] = []
    for value in quantized_signal:
        for index, concentration in enumerate(concentration_family_desc):
            if value == concentration:
                mapped_heights.append(GLUCOSE_QUANTIZATION_HEIGHTS_DESC[index])
                break
        else:
            mapped_heights.append(GLUCOSE_HEIGHTS[0])
    return mapped_heights


def _create_glucose_data(
    points: int = 1000,
    noise_scale: float = 0.7,
) -> tuple[list[np.ndarray], np.ndarray, np.ndarray, np.ndarray, np.ndarray, float, float]:
    family_curves, _, k, b = _build_reference_family(noise_scale)
    concentration_family_desc = _build_quantization_concentration_family_desc(noise_scale, k, b)

    time = np.linspace(0, 1060, points, dtype=float)
    reference_concentration = build_curve_from_control_points(
        GLUCOSE_TIME_POINTS,
        GLUCOSE_CONCENTRATION_POINTS,
        time,
    )

    quantized_signal = _quantize_reference_signal(reference_concentration, concentration_family_desc)
    heights = _map_quantized_signal_to_heights(quantized_signal, concentration_family_desc)

    raw_matrix = np.zeros((len(heights), len(GLUCOSE_FREQUENCIES)), dtype=float)
    for row_index, height in enumerate(heights):
        raw_matrix[row_index, :] = _build_hyperbola(float(height), noise_scale)

    concentration = np.array(
        [
            k * trapezoidal_integral(raw_matrix[index, :], GLUCOSE_FREQUENCIES) + b
            for index in range(raw_matrix.shape[0])
        ],
        dtype=float,
    )
    return family_curves, raw_matrix, concentration, reference_concentration, time, k, b


def generate_glucose_dataset(params: dict[str, int]) -> GeneratedDataset:
    point_count = int(params["point_count"])
    family_curves, raw_matrix, concentration, reference_concentration, time, k, b = _create_glucose_data(
        points=point_count
    )

    series: list[DataSeries] = []
    for index, curve in enumerate(family_curves, start=1):
        series.append(
            DataSeries(
                id=f"glucose_family_{index}",
                name=f"c{index}",
                x=GLUCOSE_FREQUENCIES.copy(),
                y=np.asarray(curve, dtype=float),
                editable=False,
            )
        )

    return GeneratedDataset(
        task_id="glucose_sensor",
        series=series,
        edit_model=EditModel(),
        meta={
            "frequencies": GLUCOSE_FREQUENCIES.copy(),
            "raw_matrix": raw_matrix,
            "glucose_concentration": concentration,
            "reference_concentration": reference_concentration,
            "time": time,
            "k": float(k),
            "b": float(b),
        },
    )
