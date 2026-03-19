from __future__ import annotations

from generator_app.core.models.dataset import GeneratedDataset, ProcessedView
from generator_app.core.models.edit_actions import EditAction
from generator_app.core.models.edit_model import EditProfile
from generator_app.core.models.export_model import ExportPayload
from generator_app.core.models.parameter_spec import ParameterSpec
from generator_app.core.validation.validation_result import ValidationResult
from generator_app.tasks.base.task_base import BaseSensorTask
from generator_app.tasks.test_Sin.exporter import build_export_payload
from generator_app.tasks.test_Sin.generator import generate_sine_dataset
from generator_app.tasks.test_Sin.params import build_default_parameters, build_parameter_schema
from generator_app.tasks.test_Sin.recompute import apply_edit_to_dataset


class SineSensorTask(BaseSensorTask):
    id = "sine_sensor"
    display_name = "Тестовый синус"

    def parameter_schema(self) -> list[ParameterSpec]:
        return build_parameter_schema()

    def default_parameters(self) -> dict[str, int | float]:
        return build_default_parameters()

    def validate_parameters(self, params: dict[str, int | float]) -> ValidationResult:
        errors: list[str] = []

        if int(params["point_count"]) < 3:
            errors.append("Число точек должно быть не меньше 3.")

        if float(params["time_stop"]) <= float(params["time_start"]):
            errors.append("Конец сигнала должен быть больше начала сигнала.")

        if int(params["control_point_count"]) < 2:
            errors.append("Число опорных точек должно быть не меньше 2.")

        if int(params["control_point_count"]) > int(params["point_count"]):
            errors.append("Число опорных точек не может быть больше числа точек сигнала.")

        return ValidationResult(errors=errors)

    def generate_random(self, params: dict[str, int | float]) -> GeneratedDataset:
        return generate_sine_dataset(params)

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
        return None

