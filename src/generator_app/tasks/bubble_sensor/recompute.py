from __future__ import annotations

from generator_app.core.models.dataset import GeneratedDataset
from generator_app.core.models.edit_actions import AddPointAction, EditAction, MovePointAction, RemovePointAction
from generator_app.tasks.bubble_sensor.generator import generate_bubble_dataset


def apply_edit_to_dataset(
    dataset: GeneratedDataset,
    action: EditAction,
    params: dict[str, int | float],
) -> GeneratedDataset:
    if isinstance(action, MovePointAction) and action.series_id == "bubble_control_points":
        control_points = [tuple(point) for point in dataset.meta["control_points"]]
        if action.point_index < 0 or action.point_index >= len(control_points):
            return dataset

        control_points[action.point_index] = (float(action.new_x), float(action.new_y))
        control_points.sort(key=lambda item: item[0])

        updated_params = dict(params)
        updated_params["control_points"] = control_points
        return generate_bubble_dataset(updated_params)

    if isinstance(action, AddPointAction) and action.series_id == "bubble_control_points":
        control_points = [tuple(point) for point in dataset.meta["control_points"]]
        insert_index = max(0, min(action.insert_index, len(control_points)))
        control_points.insert(insert_index, (float(action.x), float(action.y)))
        control_points.sort(key=lambda item: item[0])

        updated_params = dict(params)
        updated_params["control_points"] = control_points
        return generate_bubble_dataset(updated_params)

    if isinstance(action, RemovePointAction) and action.series_id == "bubble_control_points":
        control_points = [tuple(point) for point in dataset.meta["control_points"]]
        if action.point_index < 0 or action.point_index >= len(control_points):
            return dataset
        if len(control_points) <= 2:
            return dataset
        control_points.pop(action.point_index)

        updated_params = dict(params)
        updated_params["control_points"] = control_points
        return generate_bubble_dataset(updated_params)

    return dataset
