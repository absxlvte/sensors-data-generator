from __future__ import annotations

from generator_app.core.models.dataset import GeneratedDataset, ProcessedView
from generator_app.core.models.edit_actions import EditAction
from generator_app.core.models.edit_model import EditProfile
from generator_app.core.models.export_model import ExportPayload
from generator_app.core.models.parameter_spec import ParameterSpec
from generator_app.core.validation.validation_result import ValidationResult
from generator_app.tasks.base.task_base import BaseSensorTask
from generator_app.tasks.blood_pressure_sensor.exporter import build_export_payload
from generator_app.tasks.blood_pressure_sensor.generator import generate_blood_pressure_dataset
from generator_app.tasks.blood_pressure_sensor.params import build_default_parameters, build_parameter_schema
from generator_app.tasks.blood_pressure_sensor.processing import build_processed_view
from generator_app.tasks.blood_pressure_sensor.recompute import apply_edit_to_dataset


class BloodPressureSensorTask(BaseSensorTask):
    id = "blood_pressure_sensor"
    display_name = "Датчик артериального давления"

    def parameter_schema(self) -> list[ParameterSpec]:
        return build_parameter_schema()

    def default_parameters(self) -> dict[str, int | float]:
        return build_default_parameters()

    def validate_parameters(self, params: dict[str, int | float]) -> ValidationResult:
        errors: list[str] = []
        if float(params["duration"]) <= 0:
            errors.append("Длительность должна быть положительной.")
        if int(params["sampling_rate"]) < 100:
            errors.append("Частота дискретизации должна быть не меньше 100 Гц.")
        if int(params["dbp"]) >= int(params["sbp"]):
            errors.append("ДАД должно быть меньше САД.")
        if float(params["v_ref"]) <= 0:
            errors.append("Опорное напряжение должно быть положительным.")
        if int(params["adc_bits"]) < 8:
            errors.append("Разрядность АЦП должна быть не меньше 8 бит.")
        if float(params["k1"]) <= 0 or float(params["k2"]) <= 0:
            errors.append("Коэффициенты пересчёта должны быть положительными.")
        return ValidationResult(errors=errors)

    def generate_random(self, params: dict[str, int | float]) -> GeneratedDataset:
        return generate_blood_pressure_dataset(params)

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
