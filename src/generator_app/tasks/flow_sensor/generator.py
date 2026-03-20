from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import DataSeries, GeneratedDataset
from generator_app.core.models.edit_model import EditModel
from generator_app.plotting.pchip_adapter import build_curve_from_control_points


def _build_probability_profile(
    params: dict[str, int | float | bool | list[tuple[float, float]]],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    duration = float(params["duration"])
    sampling_rate = int(params["sampling_rate"])
    scale_factor = float(params["scale_factor"])
    control_points = sorted((float(x_value), float(y_value)) for x_value, y_value in params["control_points"])

    control_array = np.asarray(control_points, dtype=float)
    control_time = control_array[:, 0]
    control_flow = np.clip(control_array[:, 1], 0.0, None)
    control_probability = np.clip((control_flow * scale_factor) / float(sampling_rate), 0.0, 1.0)

    profile_time = np.linspace(0.0, duration, int(duration) + 1, dtype=float)
    profile_probability = build_curve_from_control_points(control_time, control_probability, profile_time)
    profile_probability = np.clip(profile_probability, 0.0, 1.0)
    return profile_time, profile_probability, control_time, control_probability


def generate_flow_dataset(
    params: dict[str, int | float | bool | list[tuple[float, float]]],
) -> GeneratedDataset:
    duration = float(params["duration"])
    sampling_rate = int(params["sampling_rate"])
    use_profile = bool(params["use_profile"])
    scale_factor = float(params["scale_factor"])
    random_probability = float(params["random_probability"])

    sample_count = max(1, int(duration * sampling_rate))
    time_axis = np.linspace(0.0, duration, sample_count, dtype=float)

    if use_profile:
        profile_time, profile_probability, control_time, control_probability = _build_probability_profile(params)
        probability = np.interp(time_axis, profile_time, profile_probability)
        probability = np.clip(probability, 0.0, 1.0)
    else:
        profile_time = np.linspace(0.0, duration, int(duration) + 1, dtype=float)
        profile_probability = np.full_like(profile_time, random_probability, dtype=float)
        control_points = sorted((float(x_value), float(y_value)) for x_value, y_value in params["control_points"])
        control_time = np.asarray([point[0] for point in control_points], dtype=float)
        control_probability = np.full_like(control_time, random_probability, dtype=float)
        probability = np.full(sample_count, random_probability, dtype=float)

    binary_signal = (np.random.random(sample_count) < probability).astype(float)
    target_flow = probability * float(sampling_rate)

    return GeneratedDataset(
        task_id="flow_sensor",
        series=[
            DataSeries(
                id="flow_binary",
                name="Импульсы датчика расхода",
                x=time_axis,
                y=binary_signal,
                editable=False,
            ),
            DataSeries(
                id="flow_probability",
                name="Вероятность срабатывания",
                x=profile_time,
                y=profile_probability,
                editable=False,
            ),
            DataSeries(
                id="flow_nodes",
                name="Опорные узлы расхода",
                x=control_time,
                y=control_probability,
                editable=True,
            ),
        ],
        edit_model=EditModel(editable_series_ids=["flow_nodes"]),
        meta={
            "time_axis": time_axis,
            "binary_signal": binary_signal,
            "profile_time": profile_time,
            "profile_probability": profile_probability,
            "control_points": list(params["control_points"]),
            "control_probability_points": list(zip(control_time.tolist(), control_probability.tolist(), strict=True)),
            "sampling_rate": sampling_rate,
            "duration": duration,
            "scale_factor": scale_factor,
            "target_flow": target_flow,
            "drag_config": {
                "flow_nodes": {
                    "x_locked": False,
                    "x_min": 0.0,
                    "x_max": duration,
                    "y_min": 0.0,
                    "y_max": 1.0,
                    "round_y": False,
                }
            },
        },
    )
