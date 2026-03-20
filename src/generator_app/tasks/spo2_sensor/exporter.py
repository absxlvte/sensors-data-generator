from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset
from generator_app.core.models.export_model import ExportColumn, ExportPayload


def build_export_payload(dataset: GeneratedDataset) -> ExportPayload:
    channel_660 = next(series for series in dataset.series if series.id == "spo2_660")
    channel_940 = next(series for series in dataset.series if series.id == "spo2_940")
    return ExportPayload(
        columns=[
            ExportColumn(
                name="time",
                values=np.asarray(channel_660.x, dtype=float),
                formatter=".6f",
            ),
            ExportColumn(
                name="z660",
                values=np.asarray(channel_660.y, dtype=float),
                formatter=".0f",
            ),
            ExportColumn(
                name="z940",
                values=np.asarray(channel_940.y, dtype=float),
                formatter=".0f",
            ),
        ]
    )
