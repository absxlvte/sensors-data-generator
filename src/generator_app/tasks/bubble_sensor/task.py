from __future__ import annotations

from generator_app.core.models.dataset import GeneratedDataset, ProcessedView
from generator_app.core.models.edit_actions import EditAction
from generator_app.core.models.edit_model import EditProfile
from generator_app.core.models.export_model import ExportPayload
from generator_app.core.models.parameter_spec import ParameterSpec
from generator_app.core.validation.validation_result import ValidationResult
from generator_app.tasks.base.task_base import BaseSensorTask
from generator_app.tasks.bubble_sensor.exporter import build_export_payload
from generator_app.tasks.bubble_sensor.generator import generate_bubble_dataset
from generator_app.tasks.bubble_sensor.params import build_default_parameters, build_parameter_schema
from generator_app.tasks.bubble_sensor.processing import build_processed_view
from generator_app.tasks.bubble_sensor.recompute import apply_edit_to_dataset


class BubbleSensorTask(BaseSensorTask):
    id = "bubble_sensor"
    display_name = "Датчик наличия пузырьков"

    def parameter_schema(self) -> list[ParameterSpec]:
        return build_parameter_schema()

    def default_parameters(self) -> dict[str, int | float]:
        return build_default_parameters()

    def validate_parameters(self, params: dict[str, int | float]) -> ValidationResult:
        errors: list[str] = []
        if int(params["point_count"]) < 10:
            errors.append("Число точек должно быть не меньше 10.")
        if float(params["time_step"]) <= 0:
            errors.append("Шаг времени должен быть положительным.")
        if float(params["distance"]) <= 0:
            errors.append("Расстояние d должно быть положительным.")
        if float(params["liquid_velocity"]) <= 0:
            errors.append("Скорость жидкости должна быть положительной.")
        if float(params["noise"]) < 0:
            errors.append("Шум не может быть отрицательным.")
        control_points = list(params["control_points"])
        if len(control_points) < 2:
            errors.append("Опорных точек должно быть не меньше двух.")
        else:
            time_values = [float(point[0]) for point in control_points]
            y_values = [float(point[1]) for point in control_points]
            if any(time_values[index] >= time_values[index + 1] for index in range(len(time_values) - 1)):
                errors.append("Время опорных точек должно строго возрастать.")
            if any(value < 0.0 or value > 0.1 for value in y_values):
                errors.append("Значения Y опорных точек должны быть в диапазоне от 0 до 0.1.")
        return ValidationResult(errors=errors)

    def generate_random(self, params: dict[str, int | float]) -> GeneratedDataset:
        return generate_bubble_dataset(params)

    def edit_profile(self, params: dict[str, int | float]) -> EditProfile:
        return EditProfile(
            mode="curve_nodes",
            allow_drag_points=True,
            allow_add_points=False,
            allow_drag_segments=False,
        )

    def apply_edit(
        self,
        dataset: GeneratedDataset,
        action: EditAction,
        params: dict[str, int | float],
    ) -> GeneratedDataset:
        return apply_edit_to_dataset(dataset, action, params)

    def build_export_payload(
        self,
        dataset: GeneratedDataset,
        params: dict[str, int | float],
    ) -> ExportPayload:
        return build_export_payload(dataset)

    def build_processed_view(
        self,
        dataset: GeneratedDataset,
        params: dict[str, int | float],
    ) -> ProcessedView | None:
        return build_processed_view(dataset)
