from __future__ import annotations

from generator_app.core.models.dataset import GeneratedDataset, ProcessedView
from generator_app.core.models.edit_actions import EditAction
from generator_app.core.models.edit_model import EditProfile
from generator_app.core.models.export_model import ExportPayload
from generator_app.core.models.parameter_spec import ParameterSpec
from generator_app.core.validation.validation_result import ValidationResult
from generator_app.tasks.base.task_base import BaseSensorTask
from generator_app.tasks.spo2_sensor.exporter import build_export_payload
from generator_app.tasks.spo2_sensor.generator import generate_spo2_dataset
from generator_app.tasks.spo2_sensor.params import build_default_parameters, build_parameter_schema
from generator_app.tasks.spo2_sensor.processing import build_processed_view
from generator_app.tasks.spo2_sensor.recompute import apply_edit_to_dataset


class SpO2SensorTask(BaseSensorTask):
    id = "spo2_sensor"
    display_name = "Датчик насыщения крови кислородом"

    def parameter_schema(self) -> list[ParameterSpec]:
        return build_parameter_schema()

    def default_parameters(self) -> dict[str, int | float]:
        return build_default_parameters()

    def validate_parameters(self, params: dict[str, int | float]) -> ValidationResult:
        errors: list[str] = []
        if not (50.0 <= float(params["spo2"]) <= 100.0):
            errors.append("SpO2 должно быть в диапазоне от 50 до 100.")
        if int(params["point_count"]) < 100:
            errors.append("Число точек должно быть не меньше 100.")
        if int(params["adc_bits"]) < 8:
            errors.append("Разрядность АЦП должна быть не меньше 8 бит.")
        if float(params["v_ref"]) <= 0:
            errors.append("Опорное напряжение должно быть положительным.")
        if float(params["coef_a"]) <= float(params["spo2"]):
            errors.append("Коэффициент A должен быть больше целевого SpO2.")
        if float(params["coef_b"]) <= 0:
            errors.append("Коэффициент B должен быть положительным.")
        return ValidationResult(errors=errors)

    def generate_random(self, params: dict[str, int | float]) -> GeneratedDataset:
        return generate_spo2_dataset(params)

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
