from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import DataSeries, GeneratedDataset
from generator_app.core.models.edit_model import ControlPoint, EditModel, EditRules
from generator_app.plotting.pchip_adapter import build_curve_from_control_points


def generate_temperature_dataset(params: dict[str, int | float]) -> GeneratedDataset:
    point_count = int(params["point_count"])
    adc_bits = int(params["adc_bits"])
    noise_sigma = float(params["noise_sigma"])
    outlier_probability = float(params["outlier_probability"])

    x = np.arange(point_count, dtype=float)
    control_x = np.array([0, point_count * 0.2, point_count * 0.45, point_count * 0.7, point_count - 1])
    control_y = np.array([20.0, 28.0, 31.0, 26.0, 24.0], dtype=float)

    temperature = build_curve_from_control_points(control_x, control_y, x)
    temperature += np.random.normal(0.0, noise_sigma, size=point_count)

    outlier_mask = np.random.random(point_count) < outlier_probability
    temperature[outlier_mask] += np.random.normal(0.0, noise_sigma * 8, size=outlier_mask.sum())

    adc_max = (2**adc_bits) - 1
    adc_values = np.clip(np.round((temperature / 50.0) * adc_max), 0, adc_max)

    edit_model = EditModel(
        control_points=[
            ControlPoint(float(x_value), float(y_value))
            for x_value, y_value in zip(control_x, control_y, strict=True)
        ],
        editable_series_ids=["temperature"],
        rules=EditRules(x_min=0, x_max=point_count - 1, y_min=0, y_max=50),
    )

    return GeneratedDataset(
        task_id="temperature_demo",
        series=[
            DataSeries(
                id="temperature",
                name="Температура",
                x=x.copy(),
                y=temperature,
                editable=True,
                unit="C",
            ),
            DataSeries(
                id="adc",
                name="Код АЦП",
                x=x.copy(),
                y=adc_values,
                editable=False,
                role="derived",
            ),
        ],
        edit_model=edit_model,
        meta={"adc_bits": adc_bits},
    )
