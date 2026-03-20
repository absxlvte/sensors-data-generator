from __future__ import annotations

from generator_app.core.models.dataset import GeneratedDataset
from generator_app.core.models.edit_actions import AddPointAction, EditAction, MovePointAction, RemovePointAction
from generator_app.tasks.blood_sensor.generator import generate_blood_dataset


def _display_to_raw_y(dataset: GeneratedDataset, display_y: float) -> float:
    adc_mapping = dataset.meta.get("adc_mapping", {})
    scale = float(adc_mapping.get("scale", 0.0))
    offset = float(adc_mapping.get("offset", 0.0))
    if scale == 0.0:
        control_points = dataset.meta.get("control_points", [])
        if control_points:
            return float(control_points[0][1])
        return float(display_y)
    return float((display_y - offset) / scale)


def apply_edit_to_dataset(
    dataset: GeneratedDataset,
    action: EditAction,
    params: dict[str, int | float | list[tuple[float, float]]],
) -> GeneratedDataset:
    control_points = [tuple(point) for point in dataset.meta.get("control_points", [])]
    if not control_points:
        return generate_blood_dataset(params, random_state=dataset.meta.get("random_state"))

    if isinstance(action, MovePointAction) and action.series_id == "blood_nodes":
        if action.point_index < 0 or action.point_index >= len(control_points):
            return dataset
        control_points[action.point_index] = (float(action.new_x), _display_to_raw_y(dataset, float(action.new_y)))
    elif isinstance(action, AddPointAction) and action.series_id == "blood_nodes":
        insert_index = max(0, min(action.insert_index, len(control_points)))
        control_points.insert(insert_index, (float(action.x), _display_to_raw_y(dataset, float(action.y))))
    elif isinstance(action, RemovePointAction) and action.series_id == "blood_nodes":
        if action.point_index < 0 or action.point_index >= len(control_points):
            return dataset
        if len(control_points) <= 2:
            return dataset
        control_points.pop(action.point_index)
    else:
        return dataset

    control_points.sort(key=lambda item: item[0])
    updated_params = dict(params)
    updated_params["control_points"] = control_points
    return generate_blood_dataset(updated_params, random_state=dataset.meta.get("random_state"))
