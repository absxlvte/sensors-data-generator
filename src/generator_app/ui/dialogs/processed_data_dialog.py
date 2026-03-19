from __future__ import annotations

import pyqtgraph as pg
from PyQt6.QtWidgets import QDialog, QVBoxLayout

from generator_app.core.models.dataset import ProcessedView


class ProcessedDataDialog(QDialog):
    _CURVE_COLORS: tuple[str, ...] = (
        "#C62828",
        "#1565C0",
        "#2E7D32",
        "#EF6C00",
        "#6A1B9A",
        "#00838F",
    )

    def __init__(self, processed_view: ProcessedView, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(processed_view.title)
        self.resize(900, 600)

        plot = pg.PlotWidget(self)
        plot.showGrid(x=True, y=True, alpha=0.25)
        plot.addLegend()
        for index, curve in enumerate(processed_view.curves):
            color = self._CURVE_COLORS[index % len(self._CURVE_COLORS)]
            plot.plot(
                curve.x,
                curve.y,
                pen=pg.mkPen(color=color, width=3),
                name=curve.name,
            )

        layout = QVBoxLayout(self)
        layout.addWidget(plot)
