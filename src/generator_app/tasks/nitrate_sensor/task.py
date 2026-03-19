from __future__ import annotations

from generator_app.core.models.dataset import GeneratedDataset, ProcessedView
from generator_app.core.models.edit_actions import EditAction
from generator_app.core.models.edit_model import EditProfile
from generator_app.core.models.export_model import ExportPayload
from generator_app.core.models.parameter_spec import ParameterSpec
from generator_app.core.validation.validation_result import ValidationResult
from generator_app.tasks.base.task_base import BaseSensorTask
from generator_app.tasks.nitrate_sensor.exporter import build_export_payload
from generator_app.tasks.nitrate_sensor.generator import PRODUCT_NAMES, generate_nitrate_dataset
from generator_app.tasks.nitrate_sensor.params import build_default_parameters, build_parameter_schema
from generator_app.tasks.nitrate_sensor.recompute import apply_edit_to_dataset


class NitrateSensorTask(BaseSensorTask):
    id = "nitrate_sensor"
    display_name = "Датчик нитратов"

    def parameter_schema(self) -> list[ParameterSpec]:
        return build_parameter_schema()

    def default_parameters(self) -> dict[str, int]:
        return build_default_parameters()

    def validate_parameters(self, params: dict[str, int]) -> ValidationResult:
        errors: list[str] = []

        if int(params["point_count"]) < 1:
            errors.append("Число точек должно быть положительным.")

        for product in PRODUCT_NAMES:
            if int(params[product]) not in {0, 1, 2}:
                errors.append(f"Для продукта {product} выбран недопустимый режим.")

        return ValidationResult(errors=errors)

    def generate_random(self, params: dict[str, int]) -> GeneratedDataset:
        return generate_nitrate_dataset(params)

    def edit_profile(self, params: dict[str, int]) -> EditProfile:
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
        params: dict[str, int],
    ) -> GeneratedDataset:
        return apply_edit_to_dataset(dataset, action, params)

    def build_export_payload(
        self,
        dataset: GeneratedDataset,
        params: dict[str, int],
    ) -> ExportPayload:
        return build_export_payload(dataset)

    def build_processed_view(
        self,
        dataset: GeneratedDataset,
        params: dict[str, int],
    ) -> ProcessedView | None:
        return None
