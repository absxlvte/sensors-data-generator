from __future__ import annotations

from typing import Any

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QSpinBox,
    QWidget,
)

from generator_app.core.models.parameter_spec import ParameterSpec
from generator_app.ui.widgets.point_list_editor import PointListEditorWidget


class ParameterFormWidget(QGroupBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Параметры", parent)
        self._layout = QFormLayout(self)
        self._editors: dict[str, QWidget] = {}

    def set_schema(self, schema: list[ParameterSpec], values: dict[str, Any]) -> None:
        while self._layout.rowCount():
            self._layout.removeRow(0)
        self._editors.clear()

        for spec in schema:
            widget = self._create_editor(spec, values.get(spec.key, spec.default))
            if spec.tooltip:
                widget.setToolTip(spec.tooltip)
            self._layout.addRow(spec.label, widget)
            self._editors[spec.key] = widget

    def collect_values(self) -> dict[str, Any]:
        values: dict[str, Any] = {}
        for key, widget in self._editors.items():
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                values[key] = widget.value()
            elif isinstance(widget, QCheckBox):
                values[key] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                values[key] = widget.currentData()
            elif isinstance(widget, PointListEditorWidget):
                values[key] = widget.value()
        return values

    def set_value(self, key: str, value: Any) -> None:
        widget = self._editors.get(key)
        if widget is None:
            return
        if isinstance(widget, QSpinBox):
            widget.setValue(int(value))
        elif isinstance(widget, QDoubleSpinBox):
            widget.setValue(float(value))
        elif isinstance(widget, QCheckBox):
            widget.setChecked(bool(value))
        elif isinstance(widget, QComboBox):
            index = widget.findData(value)
            if index >= 0:
                widget.setCurrentIndex(index)
        elif isinstance(widget, PointListEditorWidget):
            widget.set_value(value)

    def _create_editor(self, spec: ParameterSpec, value: Any) -> QWidget:
        if spec.kind == "int":
            editor = QSpinBox(self)
            editor.setRange(int(spec.min_value or 0), int(spec.max_value or 1_000_000))
            if spec.step is not None:
                editor.setSingleStep(int(spec.step))
            editor.setValue(int(value))
            return editor

        if spec.kind == "float":
            editor = QDoubleSpinBox(self)
            editor.setDecimals(6)
            editor.setRange(float(spec.min_value or -1_000_000), float(spec.max_value or 1_000_000))
            if spec.step is not None:
                editor.setSingleStep(float(spec.step))
            editor.setValue(float(value))
            return editor

        if spec.kind == "bool":
            editor = QCheckBox(self)
            editor.setChecked(bool(value))
            return editor

        if spec.kind == "choice":
            editor = QComboBox(self)
            for label, raw_value in spec.choices:
                editor.addItem(label, raw_value)
            if spec.choices:
                selected_index = next(
                    (index for index, (_, raw_value) in enumerate(spec.choices) if raw_value == value),
                    0,
                )
                editor.setCurrentIndex(selected_index)
            return editor

        if spec.kind == "point_list":
            return PointListEditorWidget(spec, value, self)

        msg = f"Unsupported parameter type: {spec.kind}"
        raise ValueError(msg)
