from __future__ import annotations

import numpy as np
import math

from generator_app.core.models.dataset import DataSeries, GeneratedDataset
from generator_app.core.models.edit_model import ControlPoint, EditModel, EditRules

def generate_sine_dataset(params: dict[str, int | float]) -> GeneratedDataset:
    point_count = int(params["point_count"])
    amplitude = float(params["amplitude"])
    frequency = float(params["frequency"])
    phase = float(params["phase"])
    y_offset = float(params["y_offset"])
    time_start = float(params["time_start"])
    time_stop = float(params["time_stop"])
    control_point_count = int(params["control_point_count"])

    x = np.linspace(time_start, time_stop, point_count, dtype=float)
    y = amplitude * np.sin(2 * math.pi * frequency * x + phase) + y_offset

    control_x = np.linspace(time_start, time_stop, control_point_count, dtype=float)
    control_y = amplitude * np.sin(2 * math.pi * frequency * control_x + phase) + y_offset

    control_points = [
        ControlPoint(float(x_value), float(y_value))
        for x_value, y_value in zip(control_x, control_y, strict=True)
    ]

    rules = EditRules(
        x_min=time_start,
        x_max=time_stop,
        y_min=y_offset - amplitude * 3,
        y_max=y_offset + amplitude * 3,
        allow_add_between_nodes=True,
    )

    edit_model = EditModel(
        control_points=control_points,
        editable_series_ids=["sine"],
        rules=rules,
    )

    signal_series = DataSeries(
        id="sine",
        name="Синусоидальный сигнал",
        x=x,
        y=y,
        editable=True,
    )

    return GeneratedDataset(
        task_id="sine_sensor",
        series=[signal_series],
        edit_model=edit_model,
        meta={},
    )