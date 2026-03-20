from generator_app.core.models.parameter_spec import ParameterSpec


DEFAULT_CONTROL_POINTS = [
    (0.0, 0.8),
    (1.0, 1.3),
    (2.5, 2.1),
    (4.0, 2.8),
    (6.0, 2.2),
    (8.0, 1.7),
    (10.0, 1.2),
]


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
            tooltip="Количество отсчетов итогового сигнала.",
        ),
        ParameterSpec(
            key="noise_level",
            label="Уровень шума",
            kind="float",
            default=0.05,
            min_value=0.0,
            max_value=1.0,
            step=0.005,
            tooltip="Интенсивность добавляемого шума.",
        ),
        ParameterSpec(
            key="outlier_count",
            label="Число выбросов",
            kind="int",
            default=5,
            min_value=0,
            max_value=200,
            step=1,
            tooltip="Сколько выбросов добавить в сигнал.",
        ),
        ParameterSpec(
            key="outlier_strength",
            label="Сила выбросов",
            kind="float",
            default=1.5,
            min_value=0.0,
            max_value=10.0,
            step=0.1,
            tooltip="Амплитуда выбросов относительно сигнала.",
        ),
        ParameterSpec(
            key="adc_bits",
            label="Разрядность АЦП",
            kind="int",
            default=10,
            min_value=4,
            max_value=24,
            step=1,
            tooltip="Число бит АЦП. Диапазон кода будет рассчитан автоматически.",
        ),
        ParameterSpec(
            key="time_start",
            label="Начало времени",
            kind="float",
            default=0.0,
            min_value=0.0,
            max_value=1000.0,
            step=0.5,
            tooltip="Начало временного интервала.",
        ),
        ParameterSpec(
            key="time_stop",
            label="Конец времени",
            kind="float",
            default=10.0,
            min_value=0.1,
            max_value=1000.0,
            step=0.5,
            tooltip="Конец временного интервала.",
        ),
        ParameterSpec(
            key="control_points",
            label="Опорные точки",
            kind="point_list",
            default=DEFAULT_CONTROL_POINTS,
            tooltip="Опорные точки исходной кривой давления.",
            x_label="Время",
            y_label="Давление",
            min_points=2,
            sort_points=True,
        ),
    ]


def build_default_parameters() -> dict[str, int | float | list[tuple[float, float]]]:
    return {
        "point_count": 1000,
        "noise_level": 0.05,
        "outlier_count": 5,
        "outlier_strength": 1.5,
        "adc_bits": 10,
        "time_start": 0.0,
        "time_stop": 10.0,
        "control_points": list(DEFAULT_CONTROL_POINTS),
    }
