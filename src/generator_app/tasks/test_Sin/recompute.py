from __future__ import annotations

from dataclasses import replace

import numpy as np

from generator_app.core.models.dataset import DataSeries, GeneratedDataset
from generator_app.core.models.edit_actions import (
    AddPointAction,
    EditAction,
    MovePointAction,
    MoveSegmentAction,
    RemovePointAction,
)
from generator_app.core.models.edit_model import ControlPoint
from generator_app.plotting.pchip_adapter import build_curve_from_control_points


def apply_edit_to_dataset(
    dataset: GeneratedDataset,
    action: EditAction,
    params: dict[str, int | float],
) -> GeneratedDataset:
    edit_model = replace(
        dataset.edit_model,
        control_points=[replace(point) for point in dataset.edit_model.control_points],
        segment_handles=list(dataset.edit_model.segment_handles),
        editable_series_ids=list(dataset.edit_model.editable_series_ids),
        rules=replace(dataset.edit_model.rules),
    )

    if isinstance(action, MovePointAction):
        point = edit_model.control_points[action.point_index]
        point.x = action.new_x
        point.y = action.new_y

    elif isinstance(action, AddPointAction):
        edit_model.control_points.insert(
            action.insert_index,
            ControlPoint(action.x, action.y),
        )

    elif isinstance(action, RemovePointAction):
        edit_model.control_points.pop(action.point_index)

    elif isinstance(action, MoveSegmentAction):
        segment = edit_model.segment_handles[action.segment_index]
        for point_index in range(segment.left_index, segment.right_index + 1):
            point = edit_model.control_points[point_index]
            point.x += action.delta_x
            point.y += action.delta_y

    control_x = np.array([point.x for point in edit_model.control_points], dtype=float)
    control_y = np.array([point.y for point in edit_model.control_points], dtype=float)

    sort_order = np.argsort(control_x)
    control_x = control_x[sort_order]
    control_y = control_y[sort_order]

    point_count = int(params["point_count"])
    time_start = float(params["time_start"])
    time_stop = float(params["time_stop"])

    x = np.linspace(time_start, time_stop, point_count, dtype=float)
    y = build_curve_from_control_points(control_x, control_y, x)

    rules = edit_model.rules
    if rules.y_min is not None:
        y = np.maximum(y, rules.y_min)
    if rules.y_max is not None:
        y = np.minimum(y, rules.y_max)

    signal_series = DataSeries(
        id="sine",
        name="Синусоидальный сигнал",
        x=x,
        y=y,
        editable=True,
    )

    return GeneratedDataset(
        task_id=dataset.task_id,
        series=[signal_series],
        edit_model=edit_model,
        meta=dict(dataset.meta),
    )
