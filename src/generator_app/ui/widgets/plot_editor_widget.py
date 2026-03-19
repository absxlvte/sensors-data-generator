from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from generator_app.core.models.dataset import DataSeries, GeneratedDataset
from generator_app.core.models.edit_actions import MovePointAction


class _DraggableSeriesItem(pg.GraphItem):
    def __init__(
        self,
        series: DataSeries,
        color: str,
        drag_config: dict[str, float | bool],
        on_point_moved,
    ) -> None:
        super().__init__()
        self._series_id = series.id
        self._series_name = series.name
        self._drag_config = drag_config
        self._on_point_moved = on_point_moved
        self._color = color
        self._positions = np.column_stack((series.x.copy(), series.y.copy()))
        self._drag_index: int | None = None
        self._drag_start: tuple[float, float] | None = None
        self._set_graph_data()

    def _set_graph_data(self) -> None:
        point_count = len(self._positions)
        adjacency = (
            np.column_stack((np.arange(point_count - 1), np.arange(1, point_count)))
            if point_count > 1
            else np.empty((0, 2), dtype=int)
        )
        self.setData(
            pos=self._positions,
            adj=adjacency,
            size=7,
            pxMode=True,
            symbol="o",
            symbolBrush=self._color,
            symbolPen=pg.mkPen(color=self._color, width=1.5),
            pen=pg.mkPen(color=self._color, width=2),
            data=np.arange(point_count),
        )

    def mouseDragEvent(self, event) -> None:  # noqa: N802 - Qt naming
        if event.button() != Qt.MouseButton.LeftButton:
            event.ignore()
            return

        if event.isStart():
            points = self.scatter.pointsAt(event.buttonDownPos())
            if not points:
                event.ignore()
                return
            point = points[0]
            self._drag_index = int(point.data())
            start_x, start_y = self._positions[self._drag_index]
            self._drag_start = (float(start_x), float(start_y))
            event.accept()
            return

        if self._drag_index is None or self._drag_start is None:
            event.ignore()
            return

        index = self._drag_index
        old_x, old_y = self._drag_start
        new_position = event.pos()

        x_locked = bool(self._drag_config.get("x_locked", False))
        y_min = self._drag_config.get("y_min")
        y_max = self._drag_config.get("y_max")
        round_y = bool(self._drag_config.get("round_y", False))

        new_x = old_x if x_locked else float(new_position.x())
        new_y = float(new_position.y())

        if y_min is not None:
            new_y = max(float(y_min), new_y)
        if y_max is not None:
            new_y = min(float(y_max), new_y)
        if round_y:
            new_y = float(round(new_y))

        self._positions[index] = [new_x, new_y]
        self._set_graph_data()
        event.accept()

        if event.isFinish():
            self._on_point_moved(
                MovePointAction(
                    series_id=self._series_id,
                    point_index=index,
                    old_x=old_x,
                    old_y=old_y,
                    new_x=new_x,
                    new_y=new_y,
                )
            )
            self._drag_index = None
            self._drag_start = None


class PlotEditorWidget(QWidget):
    point_moved = pyqtSignal(object)

    _SERIES_COLORS: dict[str, str] = {
        "Tomatoes": "#E53935",
        "Spinach": "#2E7D32",
        "Beet": "#8E244D",
        "Cabbage": "#43A047",
        "Carrot": "#FB8C00",
        "Potato": "#8D6E63",
        "Cucumbers": "#00ACC1",
        "temperature": "#D81B60",
        "adc": "#3949AB",
        "sine": "#1E88E5",
    }
    _FALLBACK_COLORS: tuple[str, ...] = (
        "#1E88E5",
        "#E53935",
        "#43A047",
        "#FB8C00",
        "#8E24AA",
        "#00897B",
        "#6D4C41",
        "#546E7A",
    )

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

        drag_config = dataset.meta.get("drag_config", {})
        editable_ids = set(dataset.edit_model.editable_series_ids)

        for index, series in enumerate(dataset.series):
            if not series.visible:
                continue
            color = self._SERIES_COLORS.get(
                series.id,
                self._FALLBACK_COLORS[index % len(self._FALLBACK_COLORS)],
            )

            series_drag_config = drag_config.get(series.id)
            if series.editable and series.id in editable_ids and series_drag_config:
                item = _DraggableSeriesItem(
                    series=series,
                    color=color,
                    drag_config=series_drag_config,
                    on_point_moved=self.point_moved.emit,
                )
                self._plot.addItem(item)
                self._plot.plot([], [], pen=pg.mkPen(color=color, width=2), name=series.name)
                continue

            self._plot.plot(
                series.x,
                series.y,
                pen=pg.mkPen(color=color, width=2),
                name=series.name,
                symbol="o" if len(series.x) <= 200 else None,
                symbolSize=5 if len(series.x) <= 200 else None,
                symbolBrush=color if len(series.x) <= 200 else None,
            )
