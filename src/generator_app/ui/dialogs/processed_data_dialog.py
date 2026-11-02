from __future__ import annotations

import pyqtgraph as pg
from pyqtgraph.exporters import ImageExporter
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

    def __init__(self, processed_view: ProcessedView, parent=None, theme: str = "dark") -> None:
        super().__init__(parent)
        self.setWindowTitle(processed_view.title)
        self.resize(900, 600)

        plot = self._build_plot(processed_view, theme, self)

        layout = QVBoxLayout(self)
        layout.addWidget(plot)

    @classmethod
    def save_png(cls, processed_view: ProcessedView, path: str, theme: str) -> None:
        plot = cls._build_plot(processed_view, theme)
        plot.resize(1600, 900)
        plot.getPlotItem().autoRange()
        exporter = ImageExporter(plot.getPlotItem())
        exporter.parameters()["width"] = 1600
        try:
            if not exporter.export(path):
                raise OSError(f"Не удалось записать PNG-файл: {path}")
        finally:
            plot.close()

    @classmethod
    def _build_plot(
        cls, processed_view: ProcessedView, theme: str, parent=None
    ) -> pg.PlotWidget:
        plot = pg.PlotWidget(parent)
        cls._apply_theme(plot, theme)
        plot.addLegend()
        for index, curve in enumerate(processed_view.curves):
            color = curve.color or cls._CURVE_COLORS[index % len(cls._CURVE_COLORS)]
            style = cls._line_style(curve.line_style)
            plot.plot(
                curve.x,
                curve.y,
                pen=pg.mkPen(color=color, width=3, style=style),
                name=curve.name,
            )
        plot.getPlotItem().autoRange()
        return plot

    @staticmethod
    def _apply_theme(plot: pg.PlotWidget, theme: str) -> None:
        if theme == "light":
            background = "#ECEFF1"
            foreground = "#1F2933"
            grid_alpha = 0.18
        else:
            background = "#111318"
            foreground = "#E5E7EB"
            grid_alpha = 0.25

        plot.setBackground(background)
        plot.showGrid(x=True, y=True, alpha=grid_alpha)
        plot_item = plot.getPlotItem()
        for axis_name in ("left", "bottom"):
            axis = plot_item.getAxis(axis_name)
            axis.setTextPen(pg.mkPen(foreground))
            axis.setPen(pg.mkPen(foreground))

    @staticmethod
    def _line_style(style_name: str):
        style_map = {
            "solid": pg.QtCore.Qt.PenStyle.SolidLine,
            "dash": pg.QtCore.Qt.PenStyle.DashLine,
            "dot": pg.QtCore.Qt.PenStyle.DotLine,
            "dash_dot": pg.QtCore.Qt.PenStyle.DashDotLine,
        }
        return style_map.get(style_name, pg.QtCore.Qt.PenStyle.SolidLine)
