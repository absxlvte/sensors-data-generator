from __future__ import annotations

from generator_app.core.models.dataset import GeneratedDataset, ProcessedView
from generator_app.core.models.edit_actions import EditAction
from generator_app.core.models.edit_model import EditProfile
from generator_app.core.models.export_model import ExportPayload
from generator_app.core.models.parameter_spec import ParameterSpec
from generator_app.core.validation.validation_result import ValidationResult
from generator_app.tasks.base.task_base import BaseSensorTask
from generator_app.tasks.ph_sensor.exporter import build_export_payload
from generator_app.tasks.ph_sensor.generator import generate_ph_dataset
from generator_app.tasks.ph_sensor.params import build_default_parameters, build_parameter_schema
from generator_app.tasks.ph_sensor.processing import build_processed_view
from generator_app.tasks.ph_sensor.recompute import apply_edit_to_dataset


class PHSensorTask(BaseSensorTask):
    id = "ph_sensor"
    display_name = "Датчик pH"

    def parameter_schema(self) -> list[ParameterSpec]:
        return build_parameter_schema()

    def default_parameters(self) -> dict[str, int | float | list[tuple[float, float]]]:
        return build_default_parameters()

    def validate_parameters(self, params: dict[str, int | float | list[tuple[float, float]]]) -> ValidationResult:
        errors: list[str] = []
        if int(params["point_count"]) < 10:
            errors.append("Число точек должно быть не меньше 10.")
        if float(params["duration"]) <= 0:
            errors.append("Длительность должна быть положительной.")
        if int(params["adc_bits"]) < 4:
            errors.append("Разрядность АЦП должна быть не меньше 4 бит.")
        if float(params["v_ref"]) <= 0:
            errors.append("Опорное напряжение должно быть положительным.")
        if float(params["temperature_k"]) <= 0:
            errors.append("Температура в K должна быть положительной.")
        if float(params["faraday_const"]) <= 0:
            errors.append("Постоянная Фарадея должна быть положительной.")
        if float(params["gas_const"]) <= 0:
            errors.append("Газовая постоянная должна быть положительной.")
        if float(params["noise_level"]) < 0:
            errors.append("Уровень шума не может быть отрицательным.")
        if int(params["outlier_count"]) < 0:
            errors.append("Число выбросов не может быть отрицательным.")
        if float(params["outlier_strength"]) < 0:
            errors.append("Сила выбросов не может быть отрицательной.")

        control_points = list(params["control_points"])
        if len(control_points) < 2:
            errors.append("Опорных точек должно быть не меньше двух.")
        else:
            time_values = [float(point[0]) for point in control_points]
            ph_values = [float(point[1]) for point in control_points]
            if any(time_values[index] >= time_values[index + 1] for index in range(len(time_values) - 1)):
                errors.append("Время опорных точек должно строго возрастать.")
            if time_values[0] < 0 or time_values[-1] > float(params["duration"]):
                errors.append("Опорные точки должны находиться внутри выбранного интервала времени.")
            if any(value < 0.1 or value > 14.0 for value in ph_values):
                errors.append("Значения pH должны быть в диапазоне от 0.1 до 14.")

        return ValidationResult(errors=errors)

    def generate_random(self, params: dict[str, int | float | list[tuple[float, float]]]) -> GeneratedDataset:
        return generate_ph_dataset(params)

    def edit_profile(self, params: dict[str, int | float | list[tuple[float, float]]]) -> EditProfile:
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
        params: dict[str, int | float | list[tuple[float, float]]],
    ) -> GeneratedDataset:
        return apply_edit_to_dataset(dataset, action, params)

    def build_export_payload(
        self,
        dataset: GeneratedDataset,
        params: dict[str, int | float | list[tuple[float, float]]],
    ) -> ExportPayload:
        return build_export_payload(dataset)

    def build_processed_view(
        self,
        dataset: GeneratedDataset,
        params: dict[str, int | float | list[tuple[float, float]]],
    ) -> ProcessedView | None:
        return build_processed_view(dataset)
