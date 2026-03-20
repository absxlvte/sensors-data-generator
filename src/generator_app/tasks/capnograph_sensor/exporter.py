from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset
from generator_app.core.models.export_model import ExportColumn, ExportPayload


def build_export_payload(dataset: GeneratedDataset) -> ExportPayload:
    time_axis = np.asarray(dataset.meta.get("time_axis", []), dtype=float)
    adc_signal = np.asarray(dataset.meta.get("adc_signal", []), dtype=float)
    return ExportPayload(
        columns=[
            ExportColumn(name="time", values=time_axis, formatter=".6f"),
            ExportColumn(name="Z", values=adc_signal, formatter=".0f"),
        ],
        delimiter=" ",
        line_ending="\n",
        encoding="utf-8",
    )
