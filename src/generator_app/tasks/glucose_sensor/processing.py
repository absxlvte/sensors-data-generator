from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset, ProcessedCurve, ProcessedView


def build_processed_view(dataset: GeneratedDataset) -> ProcessedView:
    time = np.asarray(dataset.meta["time"], dtype=float)
    frequencies = np.asarray(dataset.meta["frequencies"], dtype=float)
    k = float(dataset.meta["k"])
    b = float(dataset.meta["b"])
    raw_matrix = np.asarray(dataset.meta["raw_matrix"], dtype=float)
    reference_concentration = np.asarray(dataset.meta["reference_concentration"], dtype=float)

    concentration = np.array(
        [k * np.trapz(row, frequencies) + b for row in raw_matrix],
        dtype=float,
    )
    return ProcessedView(
        title="Концентрация глюкозы",
        curves=[
            ProcessedCurve(
                name="Эталонная динамика C(t)",
                x=time,
                y=reference_concentration,
            ),
            ProcessedCurve(
                name="Рассчитанная по площади C(t)",
                x=time,
                y=concentration,
            ),
        ],
    )
