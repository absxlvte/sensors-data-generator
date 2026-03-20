from __future__ import annotations

from generator_app.core.models.parameter_spec import ParameterSpec


def build_parameter_schema() -> list[ParameterSpec]:
    return [
        ParameterSpec(
            key="point_count",
            label="Число точек",
            kind="int",
            default=1000,
            min_value=100,
            max_value=20000,
            step=100,
            tooltip="Количество отсчетов в сигнале.",
        ),
        ParameterSpec(
            key="time_start",
            label="Начало времени",
            kind="float",
            default=0.0,
            min_value=0.0,
            max_value=1000.0,
            step=0.5,
            tooltip="Начало временной оси.",
        ),
        ParameterSpec(
            key="time_stop",
            label="Конец времени",
            kind="float",
            default=10.0,
            min_value=1.0,
            max_value=1000.0,
            step=0.5,
            tooltip="Конец временной оси.",
        ),
        ParameterSpec(
            key="adc_bits",
            label="Разрядность АЦП",
            kind="int",
            default=10,
            min_value=4,
            max_value=16,
            step=1,
            tooltip="Разрядность выходного кода АЦП.",
        ),
        ParameterSpec(
            key="noise_level",
            label="Уровень шума",
            kind="float",
            default=0.05,
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            tooltip="Относительный уровень шума.",
        ),
        ParameterSpec(
            key="outlier_count",
            label="Число выбросов",
            kind="int",
            default=0,
            min_value=0,
            max_value=1000,
            step=1,
            tooltip="Количество выбросов в сигнале.",
        ),
        ParameterSpec(
            key="outlier_strength",
            label="Сила выбросов",
            kind="float",
            default=1.5,
            min_value=0.0,
            max_value=10.0,
            step=0.1,
            tooltip="Множитель амплитуды выбросов.",
        ),
        ParameterSpec(
            key="control_points",
            label="Опорные точки",
            kind="point_list",
            default=[
                (0.0, 0.0),
                (1.0, 0.0),
                (2.0, 0.8),
                (3.5, 1.0),
                (5.0, 0.3),
                (6.0, 0.1),
                (7.5, 0.0),
                (10.0, 0.0),
            ],
            tooltip="Опорные точки формы капнограммы.",
        ),
    ]


def build_default_parameters() -> dict[str, int | float | list[tuple[float, float]]]:
    return {
        "point_count": 1000,
        "time_start": 0.0,
        "time_stop": 10.0,
        "adc_bits": 10,
        "noise_level": 0.05,
        "outlier_count": 0,
        "outlier_strength": 1.5,
        "control_points": [
            (0.0, 0.0),
            (1.0, 0.0),
            (2.0, 0.8),
            (3.5, 1.0),
            (5.0, 0.3),
            (6.0, 0.1),
            (7.5, 0.0),
            (10.0, 0.0),
        ],
    }
