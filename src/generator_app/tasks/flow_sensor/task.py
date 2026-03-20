from __future__ import annotations

from generator_app.core.models.dataset import GeneratedDataset, ProcessedView
from generator_app.core.models.edit_actions import EditAction
from generator_app.core.models.edit_model import EditProfile
from generator_app.core.models.export_model import ExportPayload
from generator_app.core.models.parameter_spec import ParameterSpec
from generator_app.core.validation.validation_result import ValidationResult
from generator_app.tasks.base.task_base import BaseSensorTask
from generator_app.tasks.flow_sensor.exporter import build_export_payload
from generator_app.tasks.flow_sensor.generator import generate_flow_dataset
from generator_app.tasks.flow_sensor.params import build_default_parameters, build_parameter_schema
from generator_app.tasks.flow_sensor.processing import build_processed_view
from generator_app.tasks.flow_sensor.recompute import apply_edit_to_dataset


class FlowSensorTask(BaseSensorTask):
    id = "flow_sensor"
    display_name = "Датчик расхода"

    def parameter_schema(self) -> list[ParameterSpec]:
        return build_parameter_schema()

    def default_parameters(self) -> dict[str, int | float | bool | list[tuple[float, float]]]:
        return build_default_parameters()

    def validate_parameters(
        self,
        params: dict[str, int | float | bool | list[tuple[float, float]]],
    ) -> ValidationResult:
        errors: list[str] = []
        if float(params["duration"]) <= 0:
            errors.append("Длительность должна быть положительной.")
        if int(params["sampling_rate"]) < 10:
            errors.append("Частота дискретизации должна быть не меньше 10 Гц.")
        if float(params["scale_factor"]) <= 0:
            errors.append("Масштаб расхода должен быть положительным.")
        if not (0.0 <= float(params["random_probability"]) <= 0.95):
            errors.append("Вероятность импульса должна быть в диапазоне от 0 до 0.95.")

        control_points = list(params["control_points"])
        if len(control_points) < 2:
            errors.append("Опорных точек расхода должно быть не меньше двух.")
        else:
            time_values = [float(point[0]) for point in control_points]
            flow_values = [float(point[1]) for point in control_points]
            if any(time_values[index] >= time_values[index + 1] for index in range(len(time_values) - 1)):
                errors.append("Время опорных точек должно строго возрастать.")
            if time_values[0] < 0 or time_values[-1] > float(params["duration"]):
                errors.append("Опорные точки должны лежать внутри выбранной длительности.")
            if any(value < 0 for value in flow_values):
                errors.append("Расход не может быть отрицательным.")
        return ValidationResult(errors=errors)

    def generate_random(
        self,
        params: dict[str, int | float | bool | list[tuple[float, float]]],
    ) -> GeneratedDataset:
        return generate_flow_dataset(params)

    def edit_profile(
        self,
        params: dict[str, int | float | bool | list[tuple[float, float]]],
    ) -> EditProfile:
        return EditProfile(
            mode="curve_nodes",
            allow_drag_points=True,
            allow_add_points=True,
            allow_drag_segments=False,
        )

    def apply_edit(
        self,
        dataset: GeneratedDataset,
        action: EditAction,
        params: dict[str, int | float | bool | list[tuple[float, float]]],
    ) -> GeneratedDataset:
        return apply_edit_to_dataset(dataset, action, params)

    def build_export_payload(
        self,
        dataset: GeneratedDataset,
        params: dict[str, int | float | bool | list[tuple[float, float]]],
    ) -> ExportPayload:
        return build_export_payload(dataset)

    def build_processed_view(
        self,
        dataset: GeneratedDataset,
        params: dict[str, int | float | bool | list[tuple[float, float]]],
    ) -> ProcessedView | None:
        return build_processed_view(dataset)
