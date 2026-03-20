from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset
from generator_app.core.models.export_model import ExportColumn, ExportPayload


def build_export_payload(dataset: GeneratedDataset) -> ExportPayload:
    signal_series = next(series for series in dataset.series if series.id == "heart_rate_signal")
    return ExportPayload(
        columns=[
            ExportColumn(
                name="time",
                values=np.asarray(signal_series.x, dtype=float),
                formatter=".6f",
            ),
            ExportColumn(
                name="voltage",
                values=np.asarray(signal_series.y, dtype=float),
                formatter=".6f",
            ),
        ]
    )
