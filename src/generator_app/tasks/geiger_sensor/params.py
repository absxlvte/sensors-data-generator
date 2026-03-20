from generator_app.core.models.parameter_spec import ParameterSpec


DEFAULT_CONTROL_POINTS = [
    (0.0, 1.0),
    (15.0, 0.2),
    (30.0, 0.8),
    (45.0, 0.0),
    (60.0, 0.0),
]


def build_parameter_schema() -> list[ParameterSpec]:
    return [
        ParameterSpec(
            key="duration",
            label="Длительность",
            kind="float",
            default=60.0,
            min_value=5.0,
            max_value=600.0,
            step=1.0,
            tooltip="Общая длительность измерения в секундах.",
        ),
        ParameterSpec(
            key="sampling_rate",
            label="Частота дискретизации",
            kind="int",
            default=1000,
            min_value=10,
            max_value=5000,
            step=10,
            tooltip="Частота дискретизации бинарного сигнала, Гц.",
        ),
        ParameterSpec(
            key="scale_factor",
            label="Масштаб частоты",
            kind="float",
            default=10.0,
            min_value=0.1,
            max_value=100.0,
            step=0.1,
            tooltip="Коэффициент масштабирования частотного профиля, как в старом проекте.",
        ),
        ParameterSpec(
            key="random_probability",
            label="Вероятность импульса",
            kind="float",
            default=0.05,
            min_value=0.0,
            max_value=0.95,
            step=0.01,
            tooltip="Используется только если опорный профиль отключён.",
        ),
        ParameterSpec(
            key="use_profile",
            label="Использовать профиль частоты",
            kind="bool",
            default=True,
            tooltip="Если отключено, генерируется случайный бинарный поток с постоянной вероятностью.",
        ),
        ParameterSpec(
            key="control_points",
            label="Опорные точки частоты",
            kind="point_list",
            default=DEFAULT_CONTROL_POINTS,
            tooltip="Задают частоту срабатывания во времени.",
            x_label="Время, с",
            y_label="Частота, Гц",
            min_points=2,
            sort_points=True,
        ),
    ]


def build_default_parameters() -> dict[str, int | float | bool | list[tuple[float, float]]]:
    return {
        "duration": 60.0,
        "sampling_rate": 1000,
        "scale_factor": 10.0,
        "random_probability": 0.05,
        "use_profile": True,
        "control_points": list(DEFAULT_CONTROL_POINTS),
    }
