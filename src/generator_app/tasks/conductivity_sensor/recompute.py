from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset
from generator_app.core.models.edit_actions import AddPointAction, EditAction, MovePointAction, RemovePointAction
from generator_app.tasks.conductivity_sensor.generator import generate_conductivity_dataset


def _display_to_raw_y(dataset: GeneratedDataset, display_y: float) -> float:
    mapping = dataset.meta.get("control_mapping", {})
    raw_min = float(mapping.get("raw_min", 0.0))
    raw_max = float(mapping.get("raw_max", 1.0))
    display_min = float(mapping.get("display_min", 0.0))
    display_max = float(mapping.get("display_max", 1.0))

    if np.isclose(display_max, display_min):
        return raw_min

    clamped_display = min(max(float(display_y), display_min), display_max)
    return raw_min + (clamped_display - display_min) * (raw_max - raw_min) / (display_max - display_min)


def apply_edit_to_dataset(
    dataset: GeneratedDataset,
    action: EditAction,
    params: dict[str, int | float | list[tuple[float, float]]],
) -> GeneratedDataset:
    control_points = [(float(x_value), float(y_value)) for x_value, y_value in dataset.meta.get("control_points", [])]
    if not control_points:
        control_points = [(float(x_value), float(y_value)) for x_value, y_value in params["control_points"]]

    if isinstance(action, MovePointAction) and action.series_id == "conductivity_nodes":
        if 0 <= action.point_index < len(control_points):
            control_points[action.point_index] = (float(action.new_x), _display_to_raw_y(dataset, float(action.new_y)))
    elif isinstance(action, AddPointAction) and action.series_id == "conductivity_nodes":
        insert_index = max(0, min(int(action.insert_index), len(control_points)))
        control_points.insert(insert_index, (float(action.x), _display_to_raw_y(dataset, float(action.y))))
    elif isinstance(action, RemovePointAction) and action.series_id == "conductivity_nodes":
        if len(control_points) > 2 and 0 <= action.point_index < len(control_points):
            control_points.pop(action.point_index)

    updated_params = dict(params)
    updated_params["control_points"] = sorted(control_points, key=lambda point: point[0])
    random_state = dataset.meta.get("random_state")
    return generate_conductivity_dataset(updated_params, random_state=random_state)
