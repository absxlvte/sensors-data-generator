from __future__ import annotations

from generator_app.core.models.dataset import GeneratedDataset, ProcessedCurve, ProcessedView


def build_processed_view(dataset: GeneratedDataset) -> ProcessedView:
    time_index = dataset.meta["time_index"]
    return ProcessedView(
        title="Сигналы пузырьков",
        curves=[
            ProcessedCurve(name="Tsend", x=time_index, y=dataset.meta["t_send"]),
            ProcessedCurve(name="Trecv", x=time_index, y=dataset.meta["t_recv"]),
        ],
    )

