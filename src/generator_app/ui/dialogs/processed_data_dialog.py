from __future__ import annotations

import pyqtgraph as pg
from PyQt6.QtWidgets import QDialog, QVBoxLayout

from generator_app.core.models.dataset import ProcessedView


class ProcessedDataDialog(QDialog):
    def __init__(self, processed_view: ProcessedView, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(processed_view.title)
        self.resize(900, 600)

        plot = pg.PlotWidget(self)
        plot.showGrid(x=True, y=True, alpha=0.25)
        plot.addLegend()
        for curve in processed_view.curves:
            plot.plot(curve.x, curve.y, pen=pg.mkPen(width=2), name=curve.name)

        layout = QVBoxLayout(self)
        layout.addWidget(plot)
