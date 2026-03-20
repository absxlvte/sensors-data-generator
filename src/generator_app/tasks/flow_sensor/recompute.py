from __future__ import annotations

from generator_app.core.models.dataset import GeneratedDataset
from generator_app.core.models.edit_actions import AddPointAction, EditAction, MovePointAction, RemovePointAction
from generator_app.tasks.flow_sensor.generator import generate_flow_dataset


def _probability_to_flow(dataset: GeneratedDataset, probability: float) -> float:
    sampling_rate = int(dataset.meta.get("sampling_rate", 1000))
    scale_factor = float(dataset.meta.get("scale_factor", 10.0))
    if scale_factor == 0:
        return 0.0
    return max(0.0, min(1.0, float(probability))) * sampling_rate / scale_factor


def apply_edit_to_dataset(
    dataset: GeneratedDataset,
    action: EditAction,
    params: dict[str, int | float | bool | list[tuple[float, float]]],
) -> GeneratedDataset:
    control_points = [tuple(point) for point in dataset.meta.get("control_points", [])]
    if not control_points:
        return generate_flow_dataset(params)

    if isinstance(action, MovePointAction) and action.series_id == "flow_nodes":
        if 0 <= action.point_index < len(control_points):
            control_points[action.point_index] = (
                float(action.new_x),
                _probability_to_flow(dataset, float(action.new_y)),
            )
        else:
            return dataset
    elif isinstance(action, AddPointAction) and action.series_id == "flow_nodes":
        insert_index = max(0, min(action.insert_index, len(control_points)))
        control_points.insert(insert_index, (float(action.x), _probability_to_flow(dataset, float(action.y))))
    elif isinstance(action, RemovePointAction) and action.series_id == "flow_nodes":
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
    return generate_flow_dataset(updated_params)
