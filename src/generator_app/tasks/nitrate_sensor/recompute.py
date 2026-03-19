from __future__ import annotations

from dataclasses import replace

import numpy as np

from generator_app.core.models.dataset import DataSeries, GeneratedDataset
from generator_app.core.models.edit_actions import EditAction, MovePointAction
from generator_app.tasks.nitrate_sensor.generator import PRODUCT_NAMES, get_state_bounds


def _copy_series(series: DataSeries) -> DataSeries:
    return replace(series, x=series.x.copy(), y=series.y.copy())


def apply_edit_to_dataset(
    dataset: GeneratedDataset,
    action: EditAction,
    params: dict[str, int],
) -> GeneratedDataset:
    if not isinstance(action, MovePointAction) or action.series_id is None:
        return dataset

    if action.series_id not in PRODUCT_NAMES:
        return dataset

    point_index = action.point_index
    series_list = [_copy_series(item) for item in dataset.series]
    target_series = next(item for item in series_list if item.id == action.series_id)

    if point_index < 0 or point_index >= len(target_series.y):
        return dataset

    y_min, y_max = get_state_bounds(action.series_id, int(params[action.series_id]))
    clamped_y = int(np.clip(round(action.new_y), y_min, y_max))
    target_series.y[point_index] = float(clamped_y)

    drag_config = dict(dataset.meta.get("drag_config", {}))
    drag_config[action.series_id] = {
        "x_locked": True,
        "y_min": float(y_min),
        "y_max": float(y_max),
        "round_y": True,
    }

    return GeneratedDataset(
        task_id=dataset.task_id,
        series=series_list,
        edit_model=replace(
            dataset.edit_model,
            editable_series_ids=list(dataset.edit_model.editable_series_ids),
        ),
        meta={
            **dataset.meta,
            "drag_config": drag_config,
        },
    )
