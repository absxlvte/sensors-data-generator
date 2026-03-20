from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset
from generator_app.core.models.export_model import ExportColumn, ExportPayload


def build_export_payload(dataset: GeneratedDataset) -> ExportPayload:
    output_series = next(series for series in dataset.series if series.id == "hydraulic_output")
    return ExportPayload(
        columns=[
            ExportColumn(
                name="time",
                values=np.asarray(output_series.x, dtype=float),
                formatter=".6f",
            ),
            ExportColumn(
                name="z",
                values=np.asarray(output_series.y, dtype=float),
                formatter=".0f",
            ),
        ]
    )
