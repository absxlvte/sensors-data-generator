from __future__ import annotations

from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from generator_app.core.models.parameter_spec import ParameterSpec


class PointListEditorWidget(QWidget):
    def __init__(self, spec: ParameterSpec, value: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._spec = spec

        self._table = QTableWidget(self)
        self._table.setColumnCount(2)
        self._table.setHorizontalHeaderLabels([spec.x_label, spec.y_label])
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked | QTableWidget.EditTrigger.SelectedClicked)
        self._table.horizontalHeader().setStretchLastSection(True)

        self._add_button = QPushButton("Добавить точку", self)
        self._remove_button = QPushButton("Удалить точку", self)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self._add_button)
        buttons_layout.addWidget(self._remove_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self._table)
        layout.addLayout(buttons_layout)

        self._add_button.clicked.connect(self._add_row)
        self._remove_button.clicked.connect(self._remove_selected_row)

        self.set_value(value)

    def set_value(self, value: Any) -> None:
        points = list(value or [])
        if self._spec.sort_points:
            points.sort(key=lambda item: item[0])
        self._table.setRowCount(0)
        for x_value, y_value in points:
            self._append_row(float(x_value), float(y_value))
        self._ensure_minimum_rows()

    def value(self) -> list[tuple[float, float]]:
        points: list[tuple[float, float]] = []
        for row in range(self._table.rowCount()):
            x_editor = self._table.cellWidget(row, 0)
            y_editor = self._table.cellWidget(row, 1)
            if not isinstance(x_editor, QDoubleSpinBox) or not isinstance(y_editor, QDoubleSpinBox):
                continue
            points.append((x_editor.value(), y_editor.value()))

        if self._spec.sort_points:
            points.sort(key=lambda item: item[0])
        return points

    def _append_row(self, x_value: float, y_value: float) -> None:
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setCellWidget(row, 0, self._create_spinbox(x_value))
        self._table.setCellWidget(row, 1, self._create_spinbox(y_value))

        for column in range(2):
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self._table.setItem(row, column, item)

    def _create_spinbox(self, value: float) -> QDoubleSpinBox:
        editor = QDoubleSpinBox(self)
        editor.setDecimals(6)
        editor.setRange(-1_000_000, 1_000_000)
        editor.setSingleStep(1.0)
        editor.setValue(value)
        return editor

    def _add_row(self) -> None:
        current_points = self.value()
        if current_points:
            last_x, last_y = current_points[-1]
            self._append_row(last_x + 1.0, last_y)
        else:
            self._append_row(0.0, 0.0)

    def _remove_selected_row(self) -> None:
        current_row = self._table.currentRow()
        if current_row < 0:
            current_row = self._table.rowCount() - 1
        if current_row < 0:
            return
        if self._table.rowCount() <= self._spec.min_points:
            return
        self._table.removeRow(current_row)
        self._ensure_minimum_rows()

    def _ensure_minimum_rows(self) -> None:
        while self._table.rowCount() < self._spec.min_points:
            if self._table.rowCount() == 0:
                self._append_row(0.0, 0.0)
            else:
                points = self.value()
                last_x, last_y = points[-1]
                self._append_row(last_x + 1.0, last_y)
