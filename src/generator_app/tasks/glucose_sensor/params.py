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
            tooltip="Количество временных отсчетов для генерации.",
        ),
    ]


def build_default_parameters() -> dict[str, int]:
    return {
        "point_count": 1000,
    }

