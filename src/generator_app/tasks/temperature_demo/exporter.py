from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset
from generator_app.core.models.export_model import ExportColumn, ExportPayload


def build_export_payload(dataset: GeneratedDataset) -> ExportPayload:
    time_axis = dataset.series[0].x
    adc_values = next(series.y for series in dataset.series if series.id == "adc")
    return ExportPayload(
        columns=[
            ExportColumn(name="time", values=np.asarray(time_axis), formatter=".0f"),
            ExportColumn(name="adc", values=np.asarray(adc_values), formatter=".0f"),
        ],
    )
