from generator_app.core.models.parameter_spec import ParameterSpec


def build_parameter_schema() -> list[ParameterSpec]:
    return [
        ParameterSpec(
            key="duration",
            label="Длительность",
            kind="float",
            default=6.0,
            min_value=1.0,
            max_value=120.0,
            step=0.5,
            tooltip="Длительность записи в секундах.",
        ),
        ParameterSpec(
            key="heart_rate",
            label="ЧСС",
            kind="int",
            default=80,
            min_value=30,
            max_value=220,
            step=1,
            tooltip="Целевая частота сердечных сокращений.",
        ),
        ParameterSpec(
            key="noise_level",
            label="Уровень шума",
            kind="float",
            default=0.1,
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            tooltip="Интенсивность шума ЭКГ-подобного сигнала.",
        ),
        ParameterSpec(
            key="sampling_rate",
            label="Частота дискретизации",
            kind="int",
            default=1000,
            min_value=100,
            max_value=5000,
            step=100,
            tooltip="Частота дискретизации сигнала в Гц.",
        ),
    ]


def build_default_parameters() -> dict[str, int | float]:
    return {
        "duration": 6.0,
        "heart_rate": 80,
        "noise_level": 0.1,
        "sampling_rate": 1000,
    }
