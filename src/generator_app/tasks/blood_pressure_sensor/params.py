from generator_app.core.models.parameter_spec import ParameterSpec


def build_parameter_schema() -> list[ParameterSpec]:
    return [
        ParameterSpec(
            key="duration",
            label="Длительность",
            kind="float",
            default=10.0,
            min_value=1.0,
            max_value=60.0,
            step=0.5,
            tooltip="Длительность записи в секундах.",
        ),
        ParameterSpec(
            key="sampling_rate",
            label="Частота дискретизации",
            kind="int",
            default=1000,
            min_value=100,
            max_value=5000,
            step=100,
            tooltip="Частота дискретизации сигнала, Гц.",
        ),
        ParameterSpec(
            key="sbp",
            label="САД",
            kind="int",
            default=120,
            min_value=60,
            max_value=250,
            step=1,
            tooltip="Систолическое артериальное давление.",
        ),
        ParameterSpec(
            key="dbp",
            label="ДАД",
            kind="int",
            default=80,
            min_value=30,
            max_value=180,
            step=1,
            tooltip="Диастолическое артериальное давление.",
        ),
        ParameterSpec(
            key="v_ref",
            label="Опорное напряжение",
            kind="float",
            default=6.0,
            min_value=0.5,
            max_value=20.0,
            step=0.1,
            tooltip="Опорное напряжение АЦП.",
        ),
        ParameterSpec(
            key="adc_bits",
            label="Разрядность АЦП",
            kind="int",
            default=12,
            min_value=8,
            max_value=24,
            step=1,
            tooltip="Число бит АЦП.",
        ),
        ParameterSpec(
            key="k1",
            label="Коэффициент САД",
            kind="float",
            default=30.0,
            min_value=1.0,
            max_value=100.0,
            step=0.5,
            tooltip="Коэффициент пересчёта систолического давления.",
        ),
        ParameterSpec(
            key="k2",
            label="Коэффициент ДАД",
            kind="float",
            default=25.0,
            min_value=1.0,
            max_value=100.0,
            step=0.5,
            tooltip="Коэффициент пересчёта диастолического давления.",
        ),
    ]


def build_default_parameters() -> dict[str, int | float]:
    return {
        "duration": 10.0,
        "sampling_rate": 1000,
        "sbp": 120,
        "dbp": 80,
        "v_ref": 6.0,
        "adc_bits": 12,
        "k1": 30.0,
        "k2": 25.0,
    }
