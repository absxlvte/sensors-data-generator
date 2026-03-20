from __future__ import annotations

from generator_app.core.models.dataset import GeneratedDataset, ProcessedView
from generator_app.core.models.edit_actions import EditAction
from generator_app.core.models.edit_model import EditProfile
from generator_app.core.models.export_model import ExportPayload
from generator_app.core.models.parameter_spec import ParameterSpec
from generator_app.core.validation.validation_result import ValidationResult
from generator_app.tasks.base.task_base import BaseSensorTask
from generator_app.tasks.liquid_level_sensor.exporter import build_export_payload
from generator_app.tasks.liquid_level_sensor.generator import generate_liquid_level_dataset
from generator_app.tasks.liquid_level_sensor.params import build_default_parameters, build_parameter_schema
from generator_app.tasks.liquid_level_sensor.processing import build_processed_view
from generator_app.tasks.liquid_level_sensor.recompute import apply_edit_to_dataset


class LiquidLevelSensorTask(BaseSensorTask):
    id = "liquid_level_sensor"
    display_name = "Датчик уровня жидкости"

    def parameter_schema(self) -> list[ParameterSpec]:
        return build_parameter_schema()

    def default_parameters(self) -> dict[str, int | float]:
        return build_default_parameters()

    def validate_parameters(self, params: dict[str, int | float]) -> ValidationResult:
        errors: list[str] = []

        if int(params["num_sensors"]) < 2:
            errors.append("Число датчиков должно быть не меньше 2.")
        if int(params["point_count"]) < 10:
            errors.append("Число точек должно быть не меньше 10.")
        if float(params["max_voltage"]) <= 0:
            errors.append("Максимальное напряжение должно быть положительным.")
        if float(params["low_voltage_min"]) < 0:
            errors.append("Минимум низкого уровня не может быть отрицательным.")
        if float(params["low_voltage_max"]) < float(params["low_voltage_min"]):
            errors.append("Максимум низкого уровня должен быть не меньше минимума.")
        if float(params["high_voltage_min"]) <= float(params["low_voltage_max"]):
            errors.append("Высокий уровень должен быть выше низкого диапазона.")
        if float(params["high_voltage_min"]) > float(params["max_voltage"]):
            errors.append("Минимум высокого уровня не может быть больше максимального напряжения.")
        if not (0.0 <= float(params["error_probability"]) <= 1.0):
            errors.append("Вероятность ошибки должна быть в диапазоне от 0 до 1.")

        return ValidationResult(errors=errors)

    def generate_random(self, params: dict[str, int | float]) -> GeneratedDataset:
        return generate_liquid_level_dataset(params)

    def edit_profile(self, params: dict[str, int | float]) -> EditProfile:
        return EditProfile(
            mode="curve_nodes",
            allow_drag_points=False,
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
