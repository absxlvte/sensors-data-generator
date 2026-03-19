from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QMenu, QVBoxLayout, QWidget

from generator_app.core.models.dataset import DataSeries, GeneratedDataset
from generator_app.core.models.edit_actions import AddPointAction, MovePointAction


class _DraggableSeriesItem(pg.GraphItem):
    def __init__(
        self,
        series: DataSeries,
        color: str,
        drag_config: dict[str, float | bool],
        on_edit_action,
    ) -> None:
        super().__init__()
        self._series_id = series.id
        self._drag_config = drag_config
        self._on_edit_action = on_edit_action
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
            pen=pg.mkPen(color=self._color, width=2.5),
            data=np.arange(point_count),
        )

    def _clamp_position(self, x_value: float, y_value: float) -> tuple[float, float]:
        x_locked = bool(self._drag_config.get("x_locked", False))
        x_min = self._drag_config.get("x_min")
        x_max = self._drag_config.get("x_max")
        y_min = self._drag_config.get("y_min")
        y_max = self._drag_config.get("y_max")
        round_y = bool(self._drag_config.get("round_y", False))

        x_result = self._positions[self._drag_index][0] if x_locked and self._drag_index is not None else x_value
        y_result = y_value

        if x_min is not None:
            x_result = max(float(x_min), x_result)
        if x_max is not None:
            x_result = min(float(x_max), x_result)
        if y_min is not None:
            y_result = max(float(y_min), y_result)
        if y_max is not None:
            y_result = min(float(y_max), y_result)
        if round_y:
            y_result = float(round(y_result))

        return float(x_result), float(y_result)

    def _build_add_action(self, x_value: float, y_value: float) -> AddPointAction | None:
        clamped_x, clamped_y = self._clamp_position(x_value, y_value)
        if len(self._positions) > 0:
            existing_x = self._positions[:, 0]
            insert_index = int(np.searchsorted(existing_x, clamped_x))
        else:
            insert_index = 0
        return AddPointAction(
            series_id=self._series_id,
            insert_index=insert_index,
            x=clamped_x,
            y=clamped_y,
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
        new_x, new_y = self._clamp_position(float(new_position.x()), float(new_position.y()))

        self._positions[index] = [new_x, new_y]
        self._set_graph_data()
        event.accept()

        if event.isFinish():
            self._on_edit_action(
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

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802 - Qt naming
        if event.button() != Qt.MouseButton.LeftButton:
            event.ignore()
            return
        action = self._build_add_action(float(event.pos().x()), float(event.pos().y()))
        if action is None:
            event.ignore()
            return
        self._on_edit_action(action)
        event.accept()

    def mouseClickEvent(self, event) -> None:  # noqa: N802 - Qt naming
        if event.button() != Qt.MouseButton.RightButton:
            event.ignore()
            return

        menu = QMenu()
        add_action = menu.addAction("Добавить узел")
        chosen_action = menu.exec(event.screenPos().toPoint())
        if chosen_action is add_action:
            action = self._build_add_action(float(event.pos().x()), float(event.pos().y()))
            if action is not None:
                self._on_edit_action(action)
                event.accept()
                return
        event.accept()


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
        "delta_t": "#1E88E5",
        "threshold": "#E53935",
        "state": "#43A047",
        "bubble_control_points": "#6A1B9A",
        "glucose_family_1": "#7B1FA2",
        "glucose_family_2": "#8E24AA",
        "glucose_family_3": "#AB47BC",
        "glucose_family_4": "#5E35B1",
        "glucose_family_5": "#3949AB",
        "glucose_family_6": "#1E88E5",
        "glucose_family_7": "#00897B",
        "glucose_family_8": "#43A047",
        "glucose_family_9": "#F4511E",
        "glucose_family_10": "#C62828",
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
                    on_edit_action=self.point_moved.emit,
                )
                self._plot.addItem(item)
                self._plot.plot([], [], pen=pg.mkPen(color=color, width=2.5), name=series.name)
                continue

            self._plot.plot(
                series.x,
                series.y,
                pen=pg.mkPen(color=color, width=2.5),
                name=series.name,
                symbol="o" if len(series.x) <= 120 else None,
                symbolSize=6 if len(series.x) <= 120 else None,
                symbolBrush=color if len(series.x) <= 200 else None,
            )
