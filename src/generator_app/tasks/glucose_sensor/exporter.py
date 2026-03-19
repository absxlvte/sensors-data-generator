from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset
from generator_app.core.models.export_model import ExportColumn, ExportPayload


def build_export_payload(dataset: GeneratedDataset) -> ExportPayload:
    raw_matrix = np.asarray(dataset.meta["raw_matrix"], dtype=float)
    frequencies = np.asarray(dataset.meta["frequencies"], dtype=float)
    time = np.asarray(dataset.meta["time"], dtype=float)

    columns = [
        ExportColumn(
            name="time",
            values=time,
            formatter=".6f",
        )
    ]

    for channel_index, frequency in enumerate(frequencies):
        columns.append(
            ExportColumn(
                name=f"Z{int(frequency)}",
                values=raw_matrix[:, channel_index],
                formatter=".0f",
            )
        )

    return ExportPayload(
        columns=columns,
        delimiter=" ",
        line_ending="\n",
        encoding="utf-8",
    )
