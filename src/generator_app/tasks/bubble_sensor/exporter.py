from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset
from generator_app.core.models.export_model import ExportColumn, ExportPayload


def build_export_payload(dataset: GeneratedDataset) -> ExportPayload:
    return ExportPayload(
        columns=[
            ExportColumn(name="time", values=np.asarray(dataset.meta["time_index"]), formatter=".0f"),
            ExportColumn(name="Tsend", values=np.asarray(dataset.meta["t_send"]), formatter=".6f"),
            ExportColumn(name="Trecv", values=np.asarray(dataset.meta["t_recv"]), formatter=".6f"),
            ExportColumn(name="delta_t", values=np.asarray(dataset.meta["delta_t"]), formatter=".6f"),
            ExportColumn(name="state", values=np.asarray(dataset.meta["state"]), formatter=".0f"),
        ],
        delimiter=" ",
        line_ending="\n",
        encoding="utf-8",
    )

