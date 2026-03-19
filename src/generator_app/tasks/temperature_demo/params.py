from generator_app.core.models.parameter_spec import ParameterSpec


def build_parameter_schema() -> list[ParameterSpec]:
    return [
        ParameterSpec(
            key="point_count",
            label="Число точек",
            kind="int",
            default=200,
            min_value=20,
            max_value=10_000,
            step=10,
        ),
        ParameterSpec(
            key="adc_bits",
            label="Разрядность АЦП",
            kind="int",
            default=12,
            min_value=8,
            max_value=24,
        ),
        ParameterSpec(
            key="noise_sigma",
            label="Шум",
            kind="float",
            default=0.15,
            min_value=0.0,
            max_value=100.0,
            step=0.01,
        ),
        ParameterSpec(
            key="outlier_probability",
            label="Вероятность выброса",
            kind="float",
            default=0.02,
            min_value=0.0,
            max_value=1.0,
            step=0.01,
        ),
    ]


def build_default_parameters() -> dict[str, int | float]:
    return {
        "point_count": 200,
        "adc_bits": 12,
        "noise_sigma": 0.15,
        "outlier_probability": 0.02,
    }
