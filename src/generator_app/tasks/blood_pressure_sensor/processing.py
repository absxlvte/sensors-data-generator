from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset, ProcessedCurve, ProcessedView


def build_processed_view(dataset: GeneratedDataset) -> ProcessedView:
    time_axis = np.asarray(dataset.meta.get("time_axis", []), dtype=float)
    target_sbp = float(dataset.meta.get("target_sbp", 0.0))
    target_dbp = float(dataset.meta.get("target_dbp", 0.0))
    estimated_sbp = float(dataset.meta.get("estimated_sbp", 0.0))
    estimated_dbp = float(dataset.meta.get("estimated_dbp", 0.0))

    return ProcessedView(
        title="Обработка артериального давления",
        curves=[
            ProcessedCurve(
                name="Заданное САД",
                x=time_axis,
                y=np.full_like(time_axis, target_sbp, dtype=float),
                color="#C62828",
                line_style="solid",
            ),
            ProcessedCurve(
                name="Рассчитанное САД",
                x=time_axis,
                y=np.full_like(time_axis, estimated_sbp, dtype=float),
                color="#C62828",
                line_style="dash",
            ),
            ProcessedCurve(
                name="Заданное ДАД",
                x=time_axis,
                y=np.full_like(time_axis, target_dbp, dtype=float),
                color="#1565C0",
                line_style="solid",
            ),
            ProcessedCurve(
                name="Рассчитанное ДАД",
                x=time_axis,
                y=np.full_like(time_axis, estimated_dbp, dtype=float),
                color="#1565C0",
                line_style="dash",
            ),
        ],
    )
