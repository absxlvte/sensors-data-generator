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
        return values

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

        msg = f"Unsupported parameter type: {spec.kind}"
        raise ValueError(msg)
