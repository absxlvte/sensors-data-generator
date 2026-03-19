from __future__ import annotations

from generator_app.core.models.dataset import GeneratedDataset, ProcessedView
from generator_app.core.models.edit_actions import EditAction
from generator_app.core.models.edit_model import EditProfile
from generator_app.core.models.export_model import ExportPayload
from generator_app.core.models.parameter_spec import ParameterSpec
from generator_app.core.validation.validation_result import ValidationResult
from generator_app.tasks.base.task_base import BaseSensorTask
from generator_app.tasks.temperature_demo.exporter import build_export_payload
from generator_app.tasks.temperature_demo.generator import generate_temperature_dataset
from generator_app.tasks.temperature_demo.params import build_default_parameters, build_parameter_schema
from generator_app.tasks.temperature_demo.processing import build_processed_view
from generator_app.tasks.temperature_demo.recompute import apply_edit_to_dataset


class TemperatureDemoTask(BaseSensorTask):
    id = "temperature_demo"
    display_name = "Датчик температуры (демо)"

    def parameter_schema(self) -> list[ParameterSpec]:
        return build_parameter_schema()

    def default_parameters(self) -> dict[str, int | float]:
        return build_default_parameters()

    def validate_parameters(self, params: dict[str, int | float]) -> ValidationResult:
        errors: list[str] = []
        if int(params["point_count"]) < 20:
            errors.append("Число точек должно быть не меньше 20.")
        if int(params["adc_bits"]) <= 0:
            errors.append("Разрядность АЦП должна быть положительной.")
        if float(params["noise_sigma"]) < 0:
            errors.append("Шум не может быть отрицательным.")
        if not 0 <= float(params["outlier_probability"]) <= 1:
            errors.append("Вероятность выброса должна быть в диапазоне от 0 до 1.")
        return ValidationResult(errors=errors)

    def generate_random(self, params: dict[str, int | float]) -> GeneratedDataset:
        return generate_temperature_dataset(params)

    def edit_profile(self, params: dict[str, int | float]) -> EditProfile:
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
