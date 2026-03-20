from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset, ProcessedCurve, ProcessedView


def build_processed_view(dataset: GeneratedDataset) -> ProcessedView:
    time_axis = np.asarray(dataset.meta.get("time_axis", []), dtype=float)
    estimated = float(dataset.meta.get("estimated_spo2", 0.0))
    target = float(dataset.meta.get("target_spo2", 0.0))
    estimated_line = np.full_like(time_axis, estimated, dtype=float)
    target_line = np.full_like(time_axis, target, dtype=float)

    return ProcessedView(
        title="Обработка SpO2",
        curves=[
            ProcessedCurve(
                name="Заданное SpO2",
                x=time_axis,
                y=target_line,
            ),
            ProcessedCurve(
                name="Рассчитанное SpO2",
                x=time_axis,
                y=estimated_line,
            ),
        ],
    )
