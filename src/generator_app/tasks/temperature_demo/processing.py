from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset, ProcessedCurve, ProcessedView


def build_processed_view(dataset: GeneratedDataset) -> ProcessedView:
    adc_series = next(series for series in dataset.series if series.id == "adc")
    adc_values = adc_series.y
    filtered = np.convolve(adc_values, np.ones(5) / 5, mode="same")
    return ProcessedView(
        title="Обработанные данные",
        curves=[
            ProcessedCurve(name="Код АЦП", x=adc_series.x, y=adc_values),
            ProcessedCurve(name="Скользящее среднее", x=adc_series.x, y=filtered),
        ],
    )
