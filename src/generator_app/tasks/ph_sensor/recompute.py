from __future__ import annotations

from generator_app.core.models.dataset import GeneratedDataset
from generator_app.core.models.edit_actions import AddPointAction, EditAction, MovePointAction, RemovePointAction
from generator_app.tasks.ph_sensor.generator import (
    _voltage_to_ph,
    _z_to_voltage_bipolar,
    generate_ph_dataset,
)


def _display_to_raw_ph(dataset: GeneratedDataset, display_y: float) -> float:
    adc_bits = int(dataset.meta.get("adc_bits", 12))
    v_ref = float(dataset.meta.get("v_ref", 5.0))
    temperature_k = float(dataset.meta.get("temperature_k", 298.0))
    faraday_const = float(dataset.meta.get("faraday_const", 96485.0))
    gas_const = float(dataset.meta.get("gas_const", 8.314))

    restored_voltage = _z_to_voltage_bipolar(round(display_y), adc_bits, v_ref)
    restored_ph = float(_voltage_to_ph(restored_voltage, temperature_k, gas_const, faraday_const))
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
