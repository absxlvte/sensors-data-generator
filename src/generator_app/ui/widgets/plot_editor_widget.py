from __future__ import annotations

import pyqtgraph as pg
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from generator_app.core.models.dataset import GeneratedDataset


class PlotEditorWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._plot = pg.PlotWidget(self)
        self._plot.showGrid(x=True, y=True, alpha=0.25)
        self._plot.addLegend()

        layout = QVBoxLayout(self)
        layout.addWidget(self._plot)

    def set_dataset(self, dataset: GeneratedDataset | None) -> None:
        self._plot.clear()
        if dataset is None:
            return

        for series in dataset.series:
            if not series.visible:
                continue
            self._plot.plot(series.x, series.y, pen=pg.mkPen(width=2), name=series.name)
