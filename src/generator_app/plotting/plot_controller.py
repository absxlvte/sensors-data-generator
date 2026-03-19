from __future__ import annotations

from generator_app.core.models.dataset import GeneratedDataset


class PlotController:
    def __init__(self) -> None:
        self._dataset: GeneratedDataset | None = None

    def set_dataset(self, dataset: GeneratedDataset | None) -> None:
        self._dataset = dataset

    @property
    def dataset(self) -> GeneratedDataset | None:
        return self._dataset
