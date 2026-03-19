from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import DataSeries, GeneratedDataset
from generator_app.core.models.edit_model import EditModel


PRODUCT_NAMES = [
    "Tomatoes",
    "Spinach",
    "Beet",
    "Cabbage",
    "Carrot",
    "Potato",
    "Cucumbers",
]

PRODUCT_RANGES: dict[str, tuple[int, int]] = {
    "Tomatoes": (33, 36),
    "Spinach": (15, 20),
    "Beet": (17, 21),
    "Cabbage": (22, 25),
    "Carrot": (25, 31),
    "Potato": (28, 33),
    "Cucumbers": (31, 33),
}

PRODUCT_LABELS: dict[str, str] = {
    "Tomatoes": "Томаты",
    "Spinach": "Шпинат",
    "Beet": "Свекла",
    "Cabbage": "Капуста",
    "Carrot": "Морковь",
    "Potato": "Картофель",
    "Cucumbers": "Огурцы",
}

HIGH_LIMIT = 85
LOW_LIMIT = 12


def _create_nitrate_values(product: str, points: int, state: str) -> np.ndarray:
    low, high = PRODUCT_RANGES[product]

    if state == "normal":
        values = np.random.randint(low, high, size=points)
    elif state == "decrease":
        values = np.random.randint(high + 1, HIGH_LIMIT, size=points)
    elif state == "increase":
        values = np.random.randint(LOW_LIMIT, low - 1, size=points)
    else:
        msg = f"Unsupported nitrate state: {state}"
        raise ValueError(msg)
    return values.astype(float)


def map_choice_to_state(choice: int) -> str:
    match choice:
        case 0:
            return "increase"
        case 1:
            return "normal"
        case 2:
            return "decrease"
        case _:
            msg = f"Unsupported nitrate choice: {choice}"
            raise ValueError(msg)


def get_state_bounds(product: str, choice: int) -> tuple[int, int]:
    low, high = PRODUCT_RANGES[product]
    state = map_choice_to_state(choice)
    if state == "normal":
        return low, high - 1
    if state == "decrease":
        return high + 1, HIGH_LIMIT - 1
    if state == "increase":
        return LOW_LIMIT, low - 2
    msg = f"Unsupported nitrate state: {state}"
    raise ValueError(msg)


def generate_nitrate_dataset(params: dict[str, int]) -> GeneratedDataset:
    point_count = int(params["point_count"])
    x = np.arange(point_count, dtype=float)

    series: list[DataSeries] = []
    export_order: list[str] = []
    state_map: dict[str, str] = {}
    drag_config: dict[str, dict[str, float | bool]] = {}

    for product in PRODUCT_NAMES:
        choice = int(params[product])
        state = map_choice_to_state(choice)
        state_map[product] = state
        values = _create_nitrate_values(product, point_count, state)
        y_min, y_max = get_state_bounds(product, choice)
        series.append(
            DataSeries(
                id=product,
                name=PRODUCT_LABELS[product],
                x=x.copy(),
                y=values,
                editable=True,
            )
        )
        export_order.append(product)
        drag_config[product] = {
            "x_locked": True,
            "y_min": float(y_min),
            "y_max": float(y_max),
            "round_y": True,
        }

    return GeneratedDataset(
        task_id="nitrate_sensor",
        series=series,
        edit_model=EditModel(editable_series_ids=list(PRODUCT_NAMES)),
        meta={
            "export_order": export_order,
            "state_map": state_map,
            "drag_config": drag_config,
        },
    )
