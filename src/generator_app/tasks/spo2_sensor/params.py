from generator_app.core.models.parameter_spec import ParameterSpec


def build_parameter_schema() -> list[ParameterSpec]:
    return [
        ParameterSpec(
            key="spo2",
            label="SpO2",
            kind="float",
            default=99.0,
            min_value=50.0,
            max_value=100.0,
            step=0.1,
            tooltip="Целевое насыщение крови кислородом.",
        ),
        ParameterSpec(
            key="point_count",
            label="Число точек",
            kind="int",
            default=1000,
            min_value=200,
            max_value=10000,
            step=100,
            tooltip="Количество отсчетов сигнала.",
        ),
        ParameterSpec(
            key="adc_bits",
            label="Разрядность АЦП",
            kind="int",
            default=16,
            min_value=8,
            max_value=24,
            step=1,
            tooltip="Число бит АЦП.",
        ),
        ParameterSpec(
            key="v_ref",
            label="Опорное напряжение",
            kind="float",
            default=5.0,
            min_value=0.1,
            max_value=20.0,
            step=0.1,
            tooltip="Опорное напряжение АЦП.",
        ),
        ParameterSpec(
            key="coef_a",
            label="Коэффициент A",
            kind="float",
            default=110.0,
            min_value=1.0,
            max_value=500.0,
            step=1.0,
            tooltip="Коэффициент формулы SpO2 = A - B * R.",
        ),
        ParameterSpec(
            key="coef_b",
            label="Коэффициент B",
            kind="float",
            default=25.0,
            min_value=0.1,
            max_value=100.0,
            step=0.1,
            tooltip="Коэффициент формулы SpO2 = A - B * R.",
        ),
    ]


def build_default_parameters() -> dict[str, int | float]:
    return {
        "spo2": 99.0,
        "point_count": 1000,
        "adc_bits": 16,
        "v_ref": 5.0,
        "coef_a": 110.0,
        "coef_b": 25.0,
    }
