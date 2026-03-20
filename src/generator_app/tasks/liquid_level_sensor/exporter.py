from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset
from generator_app.core.models.export_model import ExportColumn, ExportPayload


def build_export_payload(dataset: GeneratedDataset) -> ExportPayload:
    time_axis = np.asarray(dataset.meta.get("time_axis", []), dtype=float)
    voltage_matrix = np.asarray(dataset.meta.get("voltage_matrix", []), dtype=float)

    columns = [
        ExportColumn(
            name="time",
            values=time_axis,
            formatter=".0f",
        )
    ]

    if voltage_matrix.ndim == 2:
        for sensor_index in range(voltage_matrix.shape[1]):
            columns.append(
                ExportColumn(
                    name=f"sensor_{sensor_index + 1}",
                    values=voltage_matrix[:, sensor_index],
                    formatter=".4f",
                )
            )

    return ExportPayload(columns=columns)
