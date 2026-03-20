from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import DataSeries, GeneratedDataset
from generator_app.core.models.edit_model import EditModel


def _build_voltage_matrix(params: dict[str, int | float]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    num_sensors = int(params["num_sensors"])
    point_count = int(params["point_count"])
    max_voltage = float(params["max_voltage"])
    low_voltage_min = float(params["low_voltage_min"])
    low_voltage_max = float(params["low_voltage_max"])
    high_voltage_min = float(params["high_voltage_min"])
    error_probability = float(params["error_probability"])

    voltage_matrix = np.zeros((point_count, num_sensors), dtype=float)
    transition_points = np.zeros(num_sensors, dtype=int)

    for sensor_index in range(num_sensors):
        transition_point = int(point_count * (sensor_index + 1) / (num_sensors + 1))
        transition_points[sensor_index] = transition_point

        for state_index in range(point_count):
            if state_index < transition_point:
                voltage_matrix[state_index, sensor_index] = np.random.uniform(low_voltage_min, low_voltage_max)
            else:
                voltage_matrix[state_index, sensor_index] = np.random.uniform(high_voltage_min, max_voltage)
                if np.random.rand() < error_probability:
                    voltage_matrix[state_index, sensor_index] = np.random.uniform(low_voltage_min, low_voltage_max)

    time_axis = np.arange(1, point_count + 1, dtype=float)
    return voltage_matrix, time_axis, transition_points


def generate_liquid_level_dataset(params: dict[str, int | float]) -> GeneratedDataset:
    voltage_matrix, time_axis, transition_points = _build_voltage_matrix(params)
    num_sensors = int(params["num_sensors"])
    high_threshold = (float(params["low_voltage_max"]) + float(params["high_voltage_min"])) / 2.0

    ideal_level = np.array(
        [np.count_nonzero(sample_index >= transition_points) for sample_index in range(len(time_axis))],
        dtype=float,
    )
    detected_level = np.count_nonzero(voltage_matrix >= high_threshold, axis=1).astype(float)

    series: list[DataSeries] = []
    for sensor_index in range(num_sensors):
        series.append(
            DataSeries(
                id=f"liquid_sensor_{sensor_index + 1}",
                name=f"Датчик №{sensor_index + 1}",
                x=time_axis,
                y=voltage_matrix[:, sensor_index],
                editable=False,
            )
        )

    return GeneratedDataset(
        task_id="liquid_level_sensor",
        series=series,
        edit_model=EditModel(editable_series_ids=[]),
        meta={
            "time_axis": time_axis,
            "voltage_matrix": voltage_matrix,
            "transition_points": transition_points,
            "high_threshold": high_threshold,
            "ideal_level": ideal_level,
            "detected_level": detected_level,
        },
    )
