from generator_app.core.models.parameter_spec import ParameterSpec


def build_parameter_schema() -> list[ParameterSpec]:
    return [
        ParameterSpec(
            key="num_sensors",
            label="Число датчиков",
            kind="int",
            default=5,
            min_value=2,
            max_value=12,
            step=1,
            tooltip="Количество дискретных датчиков уровня.",
        ),
        ParameterSpec(
            key="point_count",
            label="Число точек",
            kind="int",
            default=50,
            min_value=10,
            max_value=5000,
            step=10,
            tooltip="Количество отсчётов во времени.",
        ),
        ParameterSpec(
            key="max_voltage",
            label="Максимальное напряжение",
            kind="float",
            default=5.0,
            min_value=1.0,
            max_value=20.0,
            step=0.1,
            tooltip="Верхний уровень напряжения активного датчика.",
        ),
        ParameterSpec(
            key="low_voltage_min",
            label="Мин. низкого уровня",
            kind="float",
            default=0.0,
            min_value=0.0,
            max_value=2.0,
            step=0.01,
            tooltip="Нижняя граница шума при неактивном датчике.",
        ),
        ParameterSpec(
            key="low_voltage_max",
            label="Макс. низкого уровня",
            kind="float",
            default=0.2,
            min_value=0.0,
            max_value=2.0,
            step=0.01,
            tooltip="Верхняя граница шума при неактивном датчике.",
        ),
        ParameterSpec(
            key="high_voltage_min",
            label="Мин. высокого уровня",
            kind="float",
            default=4.8,
            min_value=0.5,
            max_value=20.0,
            step=0.1,
            tooltip="Нижняя граница напряжения после срабатывания датчика.",
        ),
        ParameterSpec(
            key="error_probability",
            label="Вероятность ошибки",
            kind="float",
            default=0.05,
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            tooltip="Вероятность ложного провала в высоком уровне.",
        ),
    ]


def build_default_parameters() -> dict[str, int | float]:
    return {
        "num_sensors": 5,
        "point_count": 50,
        "max_voltage": 5.0,
        "low_voltage_min": 0.0,
        "low_voltage_max": 0.2,
        "high_voltage_min": 4.8,
        "error_probability": 0.05,
    }
