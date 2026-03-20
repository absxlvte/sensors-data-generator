from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset
from generator_app.core.models.export_model import ExportColumn, ExportPayload


def build_export_payload(dataset: GeneratedDataset) -> ExportPayload:
    return ExportPayload(
        columns=[
            ExportColumn(
                name="time",
                values=np.asarray(dataset.meta.get("time_axis", []), dtype=float),
                formatter=".6f",
            ),
            ExportColumn(
                name="z",
                values=np.asarray(dataset.meta.get("adc_signal", []), dtype=float),
                formatter=".0f",
            ),
        ]
    )
