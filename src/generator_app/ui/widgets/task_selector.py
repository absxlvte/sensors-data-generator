from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QComboBox, QVBoxLayout, QWidget

from generator_app.core.interfaces.sensor_task import SensorTask


class TaskSelectorWidget(QWidget):
    task_changed = pyqtSignal(str)

    def __init__(self, tasks: list[SensorTask], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._combo = QComboBox(self)
        for task in tasks:
            self._combo.addItem(task.display_name, task.id)

        layout = QVBoxLayout(self)
        layout.addWidget(self._combo)
        self._combo.currentIndexChanged.connect(self._emit_change)

    def _emit_change(self) -> None:
        self.task_changed.emit(self.current_task_id())

    def current_task_id(self) -> str:
        return str(self._combo.currentData())
