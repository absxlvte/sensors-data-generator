from __future__ import annotations

from generator_app.core.models.dataset import GeneratedDataset, ProcessedView
from generator_app.core.models.edit_actions import EditAction
from generator_app.core.models.edit_model import EditProfile
from generator_app.core.models.export_model import ExportPayload
from generator_app.core.models.parameter_spec import ParameterSpec
from generator_app.core.validation.validation_result import ValidationResult
from generator_app.tasks.base.task_base import BaseSensorTask
from generator_app.tasks.heart_rate_sensor.exporter import build_export_payload
from generator_app.tasks.heart_rate_sensor.generator import generate_heart_rate_dataset
from generator_app.tasks.heart_rate_sensor.params import build_default_parameters, build_parameter_schema
from generator_app.tasks.heart_rate_sensor.processing import build_processed_view
from generator_app.tasks.heart_rate_sensor.recompute import apply_edit_to_dataset


class HeartRateSensorTask(BaseSensorTask):
    id = "heart_rate_sensor"
    display_name = "Датчик ЧСС"

    def parameter_schema(self) -> list[ParameterSpec]:
        return build_parameter_schema()

    def default_parameters(self) -> dict[str, int | float]:
        return build_default_parameters()

    def validate_parameters(self, params: dict[str, int | float]) -> ValidationResult:
        errors: list[str] = []
        if float(params["duration"]) <= 0:
            errors.append("Длительность должна быть положительной.")
        if int(params["heart_rate"]) <= 0:
            errors.append("ЧСС должна быть положительной.")
        if float(params["noise_level"]) < 0:
            errors.append("Уровень шума не может быть отрицательным.")
        if int(params["sampling_rate"]) < 100:
            errors.append("Частота дискретизации должна быть не меньше 100 Гц.")
        return ValidationResult(errors=errors)

    def generate_random(self, params: dict[str, int | float]) -> GeneratedDataset:
        return generate_heart_rate_dataset(params)

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
