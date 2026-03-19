import math

from generator_app.core.models.parameter_spec import ParameterSpec


def build_parameter_schema() -> list[ParameterSpec]:
    return [
        ParameterSpec(
            key="point_count",
            label="Число точек",
            kind="int",
            default=1000,
            min_value=100,
            max_value=10_000,
            step=100,
            tooltip="Число точек"
        ),
        ParameterSpec(
            key="amplitude",
            label="Амплитуда",
            kind="float",
            default=1.0,
            min_value=0.1,
            max_value=10.0,
            step=0.1,
            tooltip="Амплитуда сигнала"
        ),
        ParameterSpec(
            key="frequency",
            label="Частота",
            kind="float",
            default=1.0,
            min_value=0.1,
            max_value=10.0,
            step=0.05,
            tooltip="Частота сигнала"
        ),
        ParameterSpec(
            key="phase",
            label="Фаза",
            kind="float",
            default=0.0,
            min_value=-math.pi/2,
            max_value=+math.pi/2,
            step=math.pi/8,
            tooltip="Фаза сигнала"
        ),
        ParameterSpec(
            key="y_offset",
            label="Смещение по оси Y",
            kind="float",
            default=0.0,
            min_value=-10.0,
            max_value=10.0,
            step=0.1,
            tooltip="смещение по Y"
        ),
        ParameterSpec(
            key="time_start",
            label="Начало сигнала",
            kind="float",
            default=0.0,
            min_value=0.0,
            max_value=100.0,
            step=1.0,
            tooltip="старт сигнала"
        ),
        ParameterSpec(
            key="time_stop",
            label="Конец сигнала",
            kind="float",
            default=10.0,
            min_value=10.0,
            max_value=100.0,
            step=1.0,
            tooltip="конец сигнала"
        ),
        ParameterSpec(
            key="control_point_count",
            label="Число точек для перемещения",
            kind="int",
            default=10,
            min_value=1,
            max_value=100,
            step=1,
            tooltip="число точек, которые можно двигать"
        ),
    ]


def build_default_parameters() -> dict[str, int | float]:
    return {
        "point_count": 1000,
        "amplitude": 1.0,
        "frequency": 1.0,
        "phase": 0.0,
        "y_offset": 0.0,
        "time_start": 0.0,
        "time_stop": 10.0,
        "control_point_count": 10
    }
