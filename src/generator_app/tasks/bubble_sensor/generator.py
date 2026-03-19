from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import DataSeries, GeneratedDataset
from generator_app.core.models.edit_model import EditModel
from generator_app.plotting.pchip_adapter import build_curve_from_control_points

CONTROL_POINT_Y_MAX = 0.1


def _scale_signal(signal: np.ndarray, target_min: float, target_max: float, offset: float = 0.0) -> np.ndarray:
    signal = np.asarray(signal, dtype=float)
    current_min = float(np.min(signal))
    current_max = float(np.max(signal))
    current_amplitude = current_max - current_min
    target_amplitude = target_max - target_min

    if current_amplitude == 0:
        return np.full_like(signal, (target_min + target_max) / 2 + offset)

    current_center = (current_max + current_min) / 2
    target_center = (target_max + target_min) / 2
    scaled = (signal - current_center) * (target_amplitude / current_amplitude) + target_center
    return scaled + offset


def _bubble_create(
    points: int,
    time_step: float,
    distance: float,
    liquid_velocity: float,
    noise: float,
    control_points: list[tuple[float, float]],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    t_liq = distance / liquid_velocity
    time_new = np.linspace(0, points * time_step, points, dtype=float)
    control_array = np.asarray(control_points, dtype=float)
    control_time = control_array[:, 0]
    control_value = np.clip(control_array[:, 1], 0.0, CONTROL_POINT_Y_MAX)
    delta_t = build_curve_from_control_points(control_time, control_value, time_new)
    delta_t = _scale_signal(delta_t, t_liq, 1.0)

    t_send = (
        time_new
        + t_liq * np.random.uniform(1.0, 1.5, size=len(time_new))
        + noise * np.random.normal(size=len(time_new)) * np.max(np.abs(time_new))
    )
    t_recv = t_send + delta_t
    t_recv = np.clip(t_recv, 0, np.max(t_recv))
    t_send = np.clip(t_send, 0, np.max(t_recv))
    state = (delta_t > 1.1 * t_liq).astype(float)
    threshold = np.full_like(delta_t, t_liq, dtype=float)
    return t_send, t_recv, state, delta_t, threshold, time_new


def generate_bubble_dataset(params: dict[str, int | float]) -> GeneratedDataset:
    point_count = int(params["point_count"])
    time_step = float(params["time_step"])
    distance = float(params["distance"])
    liquid_velocity = float(params["liquid_velocity"])
    noise = float(params["noise"])
    control_points = list(params["control_points"])

    t_send, t_recv, state, delta_t, threshold, time_axis = _bubble_create(
        points=point_count,
        time_step=time_step,
        distance=distance,
        liquid_velocity=liquid_velocity,
        noise=noise,
        control_points=control_points,
    )
    control_array = np.asarray(control_points, dtype=float)
    control_array[:, 1] = np.clip(control_array[:, 1], 0.0, CONTROL_POINT_Y_MAX)
    total_time = float(point_count * time_step)

    return GeneratedDataset(
        task_id="bubble_sensor",
        series=[
            DataSeries(
                id="delta_t",
                name="delta_t",
                x=time_axis.copy(),
                y=delta_t,
                editable=False,
            ),
            DataSeries(
                id="threshold",
                name="Порог d/Vliq",
                x=time_axis.copy(),
                y=threshold,
                editable=False,
            ),
            DataSeries(
                id="state",
                name="Состояние пузырька",
                x=time_axis.copy(),
                y=state,
                editable=False,
            ),
            DataSeries(
                id="bubble_control_points",
                name="Опорные точки",
                x=control_array[:, 0].copy(),
                y=control_array[:, 1].copy(),
                editable=True,
            ),
        ],
        edit_model=EditModel(editable_series_ids=["bubble_control_points"]),
        meta={
            "time_index": time_axis,
            "t_send": t_send,
            "t_recv": t_recv,
            "delta_t": delta_t,
            "state": state,
            "threshold": threshold,
            "control_points": control_points,
            "drag_config": {
                "bubble_control_points": {
                    "x_locked": False,
                    "x_min": 0.0,
                    "x_max": total_time,
                    "y_min": 0.0,
                    "y_max": CONTROL_POINT_Y_MAX,
                    "round_y": False,
                }
            },
        },
    )
