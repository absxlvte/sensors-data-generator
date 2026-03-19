from generator_app.core.models.parameter_spec import ParameterSpec


DEFAULT_TIME_POINTS = [0, 50, 100, 150, 250, 400, 450, 500, 550, 600, 700, 900, 950, 1000]
DEFAULT_VALUE_POINTS = [0, 7, 4, 5, 0, 0, 2, 2, 3, 1, 1, 5, 5, 0]
DEFAULT_MAX_CONTROL_VALUE = 0.1


def _normalize_values(values: list[float], target_max: float) -> list[float]:
    max_value = max(values) if values else 1.0
    if max_value == 0:
        return [0.0 for _ in values]
    return [value * target_max / max_value for value in values]


DEFAULT_CONTROL_VALUES = _normalize_values(DEFAULT_VALUE_POINTS, DEFAULT_MAX_CONTROL_VALUE)
DEFAULT_CONTROL_POINTS = list(zip(DEFAULT_TIME_POINTS, DEFAULT_CONTROL_VALUES, strict=True))


def build_parameter_schema() -> list[ParameterSpec]:
    return [
        ParameterSpec(
            key="point_count",
            label="Число точек",
            kind="int",
            default=1000,
            min_value=100,
            max_value=10000,
            step=100,
            tooltip="Количество отсчетов сигнала.",
        ),
        ParameterSpec(
            key="time_step",
            label="Шаг времени",
            kind="float",
            default=1.0,
            min_value=0.01,
            max_value=100.0,
            step=0.1,
            tooltip="Шаг по времени между отсчетами.",
        ),
        ParameterSpec(
            key="distance",
            label="Расстояние d",
            kind="float",
            default=0.1,
            min_value=0.001,
            max_value=10.0,
            step=0.01,
            tooltip="Расстояние между излучателем и приемником.",
        ),
        ParameterSpec(
            key="liquid_velocity",
            label="Скорость жидкости",
            kind="float",
            default=1.4,
            min_value=0.01,
            max_value=100.0,
            step=0.01,
            tooltip="Скорость распространения сигнала в жидкости.",
        ),
        ParameterSpec(
            key="noise",
            label="Шум",
            kind="float",
            default=0.01,
            min_value=0.0,
            max_value=1.0,
            step=0.001,
            tooltip="Уровень добавляемого шума.",
        ),
        ParameterSpec(
            key="control_points",
            label="Опорные точки",
            kind="point_list",
            default=DEFAULT_CONTROL_POINTS,
            tooltip="Опорные точки сценария появления пузырьков.",
            x_label="Время",
            y_label="Амплитуда",
            min_points=2,
            sort_points=True,
        ),
    ]


def build_default_parameters() -> dict[str, int | float | list[tuple[float, float]]]:
    return {
        "point_count": 1000,
        "time_step": 1.0,
        "distance": 0.1,
        "liquid_velocity": 1.4,
        "noise": 0.01,
        "control_points": list(DEFAULT_CONTROL_POINTS),
    }
