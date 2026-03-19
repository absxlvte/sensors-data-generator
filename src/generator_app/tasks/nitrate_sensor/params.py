from generator_app.core.models.parameter_spec import ParameterSpec


PRODUCT_STATE_CHOICES = [
    ("Повышение", 0),
    ("Норма", 1),
    ("Понижение", 2),
]


def build_parameter_schema() -> list[ParameterSpec]:
    return [
        ParameterSpec(
            key="point_count",
            label="Число точек",
            kind="int",
            default=100,
            min_value=10,
            max_value=10_000,
            step=10,
            tooltip="Количество отсчетов для каждого продукта.",
        ),
        ParameterSpec(
            key="Tomatoes",
            label="Томаты",
            kind="choice",
            default=1,
            choices=PRODUCT_STATE_CHOICES,
            tooltip="Режим генерации для томатов.",
        ),
        ParameterSpec(
            key="Spinach",
            label="Шпинат",
            kind="choice",
            default=1,
            choices=PRODUCT_STATE_CHOICES,
            tooltip="Режим генерации для шпината.",
        ),
        ParameterSpec(
            key="Beet",
            label="Свекла",
            kind="choice",
            default=1,
            choices=PRODUCT_STATE_CHOICES,
            tooltip="Режим генерации для свеклы.",
        ),
        ParameterSpec(
            key="Cabbage",
            label="Капуста",
            kind="choice",
            default=1,
            choices=PRODUCT_STATE_CHOICES,
            tooltip="Режим генерации для капусты.",
        ),
        ParameterSpec(
            key="Carrot",
            label="Морковь",
            kind="choice",
            default=1,
            choices=PRODUCT_STATE_CHOICES,
            tooltip="Режим генерации для моркови.",
        ),
        ParameterSpec(
            key="Potato",
            label="Картофель",
            kind="choice",
            default=1,
            choices=PRODUCT_STATE_CHOICES,
            tooltip="Режим генерации для картофеля.",
        ),
        ParameterSpec(
            key="Cucumbers",
            label="Огурцы",
            kind="choice",
            default=1,
            choices=PRODUCT_STATE_CHOICES,
            tooltip="Режим генерации для огурцов.",
        ),
    ]


def build_default_parameters() -> dict[str, int]:
    return {
        "point_count": 100,
        "Tomatoes": 1,
        "Spinach": 1,
        "Beet": 1,
        "Cabbage": 1,
        "Carrot": 1,
        "Potato": 1,
        "Cucumbers": 1,
    }

