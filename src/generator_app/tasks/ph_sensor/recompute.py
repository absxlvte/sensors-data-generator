from __future__ import annotations

from generator_app.core.models.dataset import GeneratedDataset
from generator_app.core.models.edit_actions import AddPointAction, EditAction, MovePointAction, RemovePointAction
from generator_app.tasks.ph_sensor.generator import generate_ph_dataset


def _display_to_raw_ph(dataset: GeneratedDataset, display_y: float) -> float:
    adc_mapping = dataset.meta.get("adc_mapping", {})
    scale = float(adc_mapping.get("scale", 0.0))
    offset = float(adc_mapping.get("offset", 0.0))
    if scale == 0.0:
        restored_ph = float(adc_mapping.get("raw_min", 7.0))
    else:
        restored_ph = (float(display_y) - offset) / scale
    return float(min(14.0, max(0.1, restored_ph)))


def apply_edit_to_dataset(
    dataset: GeneratedDataset,
    action: EditAction,
    params: dict[str, int | float | list[tuple[float, float]]],
) -> GeneratedDataset:
    control_points = [tuple(point) for point in dataset.meta.get("control_points", [])]
    if not control_points:
        return generate_ph_dataset(params, random_state=dataset.meta.get("random_state"))

    if isinstance(action, MovePointAction) and action.series_id == "ph_nodes":
        if 0 <= action.point_index < len(control_points):
            control_points[action.point_index] = (float(action.new_x), _display_to_raw_ph(dataset, float(action.new_y)))
        else:
            return dataset
    elif isinstance(action, AddPointAction) and action.series_id == "ph_nodes":
        insert_index = max(0, min(action.insert_index, len(control_points)))
        control_points.insert(insert_index, (float(action.x), _display_to_raw_ph(dataset, float(action.y))))
    elif isinstance(action, RemovePointAction) and action.series_id == "ph_nodes":
        if 0 <= action.point_index < len(control_points):
            if len(control_points) <= 2:
                return dataset
            control_points.pop(action.point_index)
        else:
            return dataset
    else:
        return dataset

    control_points.sort(key=lambda item: item[0])
    updated_params = dict(params)
    updated_params["control_points"] = control_points
    return generate_ph_dataset(updated_params, random_state=dataset.meta.get("random_state"))
