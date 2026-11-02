from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from pyqtgraph.exporters import ImageExporter
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QMenu, QVBoxLayout, QWidget

from generator_app.core.models.dataset import DataSeries, GeneratedDataset
from generator_app.core.models.edit_actions import AddPointAction, MovePointAction, RemovePointAction


class _DraggableSeriesItem(pg.GraphItem):
    def __init__(
        self,
        series: DataSeries,
        color: str,
        drag_config: dict[str, float | bool],
        on_edit_action,
        on_selection_changed,
        selected_index: int | None = None,
    ) -> None:
        super().__init__()
        self._series_id = series.id
        self._drag_config = drag_config
        self._on_edit_action = on_edit_action
        self._on_selection_changed = on_selection_changed
        self._color = color
        self._positions = np.column_stack((series.x.copy(), series.y.copy()))
        self._drag_index: int | None = None
        self._drag_start: tuple[float, float] | None = None
        self._selected_index: int | None = selected_index
        self._set_graph_data()

    def _set_graph_data(self) -> None:
        point_count = len(self._positions)
        adjacency = (
            np.column_stack((np.arange(point_count - 1), np.arange(1, point_count)))
            if point_count > 1
            else np.empty((0, 2), dtype=int)
        )
        symbol_sizes = [7] * point_count
        symbol_brushes = [pg.mkBrush(self._color)] * point_count
        symbol_pens = [pg.mkPen(color=self._color, width=1.5)] * point_count

        if self._selected_index is not None and 0 <= self._selected_index < point_count:
            symbol_sizes[self._selected_index] = 11
            symbol_brushes[self._selected_index] = pg.mkBrush("#FFF176")
            symbol_pens[self._selected_index] = pg.mkPen(color="#1A1A1A", width=2.0)

        if self._drag_index is not None and 0 <= self._drag_index < point_count:
            symbol_sizes[self._drag_index] = 14
            symbol_brushes[self._drag_index] = pg.mkBrush("#FF5252")
            symbol_pens[self._drag_index] = pg.mkPen(color="#FFFFFF", width=2.5)

        self.setData(
            pos=self._positions,
            adj=adjacency,
            size=symbol_sizes,
            pxMode=True,
            symbol="o",
            symbolBrush=symbol_brushes,
            symbolPen=symbol_pens,
            pen=pg.mkPen(color=self._color, width=2.5),
            data=np.arange(point_count),
        )

    def _select_index(self, index: int | None) -> None:
        self._selected_index = index
        self._on_selection_changed(self._series_id, index)
        self._set_graph_data()

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

    def _build_add_action(self, x_value: float, y_value: float) -> AddPointAction:
        clamped_x, clamped_y = self._clamp_position(x_value, y_value)
        existing_x = self._positions[:, 0] if len(self._positions) > 0 else np.array([], dtype=float)
        insert_index = int(np.searchsorted(existing_x, clamped_x))
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
            if len(points) == 0:
                event.ignore()
                return
            point = points[0]
            self._drag_index = int(point.data())
            self._select_index(self._drag_index)
            start_x, start_y = self._positions[self._drag_index]
            self._drag_start = (float(start_x), float(start_y))
            self._set_graph_data()
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
            self._selected_index = index
            self._drag_index = None
            self._drag_start = None
            self._set_graph_data()

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802 - Qt naming
        if event.button() != Qt.MouseButton.LeftButton:
            event.ignore()
            return
        self._on_edit_action(self._build_add_action(float(event.pos().x()), float(event.pos().y())))
        event.accept()

    def mouseClickEvent(self, event) -> None:  # noqa: N802 - Qt naming
        clicked_points = self.scatter.pointsAt(event.pos())
        clicked_index = int(clicked_points[0].data()) if len(clicked_points) > 0 else None

        if event.button() == Qt.MouseButton.LeftButton:
            self._select_index(clicked_index)
            event.accept()
            return

        if event.button() != Qt.MouseButton.RightButton:
            event.ignore()
            return

        self._select_index(clicked_index)

        menu = QMenu()
        add_action = menu.addAction("Добавить узел")
        remove_action = menu.addAction("Удалить узел") if clicked_index is not None else None
        chosen_action = menu.exec(event.screenPos().toPoint())

        if chosen_action is add_action:
            self._on_edit_action(self._build_add_action(float(event.pos().x()), float(event.pos().y())))
            event.accept()
            return

        if remove_action is not None and chosen_action is remove_action and clicked_index is not None:
            point_x, point_y = self._positions[clicked_index]
            self._on_edit_action(
                RemovePointAction(
                    series_id=self._series_id,
                    point_index=clicked_index,
                    x=float(point_x),
                    y=float(point_y),
                )
            )
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
        "temperature_output": "#D81B60",
        "temperature_reference": "#FB8C00",
        "temperature_nodes": "#3949AB",
        "capnograph_output": "#00695C",
        "capnograph_reference": "#FB8C00",
        "capnograph_nodes": "#C62828",
        "conductivity_output": "#283593",
        "conductivity_reference": "#00897B",
        "conductivity_nodes": "#EF6C00",
        "hydraulic_output": "#00897B",
        "hydraulic_reference": "#F4511E",
        "hydraulic_nodes": "#5E35B1",
        "blood_output": "#C62828",
        "blood_reference": "#1565C0",
        "blood_nodes": "#6A1B9A",
        "blood_pressure_output": "#8E24AA",
        "ph_output": "#6D4C41",
        "ph_reference": "#00897B",
        "ph_nodes": "#5E35B1",
        "ph_acidic": "#E53935",
        "ph_neutral": "#546E7A",
        "ph_alkaline": "#43A047",
        "spo2_660": "#1E88E5",
        "spo2_940": "#43A047",
        "heart_rate_signal": "#D81B60",
        "adc": "#3949AB",
        "sine": "#1E88E5",
        "delta_t": "#1E88E5",
        "threshold": "#E53935",
        "state": "#43A047",
        "bubble_control_points": "#6A1B9A",
        "geiger_binary": "#3949AB",
        "geiger_probability": "#E53935",
        "geiger_nodes": "#00897B",
        "flow_binary": "#5E35B1",
        "flow_probability": "#F4511E",
        "flow_nodes": "#00897B",
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
        self._theme = "dark"
        self._plot.showGrid(x=True, y=True, alpha=0.25)
        self._plot.addLegend()
        self._selected_points: dict[str, int | None] = {}
        self.set_theme(self._theme)

        layout = QVBoxLayout(self)
        layout.addWidget(self._plot)

    def set_theme(self, theme: str) -> None:
        self._theme = theme
        if theme == "light":
            background = "#ECEFF1"
            foreground = "#1F2933"
            grid_alpha = 0.18
        else:
            background = "#111318"
            foreground = "#E5E7EB"
            grid_alpha = 0.25

        self._plot.setBackground(background)
        self._plot.showGrid(x=True, y=True, alpha=grid_alpha)
        plot_item = self._plot.getPlotItem()
        for axis_name in ("left", "bottom"):
            axis = plot_item.getAxis(axis_name)
            axis.setTextPen(pg.mkPen(foreground))
            axis.setPen(pg.mkPen(foreground))

    def _handle_selection_changed(self, series_id: str, point_index: int | None) -> None:
        self._selected_points[series_id] = point_index

    def set_dataset(self, dataset: GeneratedDataset | None) -> None:
        self._plot.clear()
        if dataset is None:
            self._selected_points.clear()
            self._plot.getViewBox().autoRange()
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
                    on_selection_changed=self._handle_selection_changed,
                    selected_index=self._selected_points.get(series.id),
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

        self._plot.getViewBox().autoRange()

    def save_png(self, path: str) -> None:
        exporter = ImageExporter(self._plot.getPlotItem())
        exporter.parameters()["width"] = 1600
        if not exporter.export(path):
            raise OSError(f"Не удалось записать PNG-файл: {path}")
