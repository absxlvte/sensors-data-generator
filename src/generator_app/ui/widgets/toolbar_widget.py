from __future__ import annotations

from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QPushButton, QWidget


class ToolbarWidget(QGroupBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Редактирование", parent)
        layout = QHBoxLayout(self)
        self.move_point_button = QPushButton("Узел", self)
        self.add_point_button = QPushButton("Добавить узел", self)
        self.move_segment_button = QPushButton("Сегмент", self)
        self.undo_button = QPushButton("Отменить", self)
        self.redo_button = QPushButton("Повторить", self)

        layout.addWidget(self.move_point_button)
        layout.addWidget(self.add_point_button)
        layout.addWidget(self.move_segment_button)
        layout.addWidget(self.undo_button)
        layout.addWidget(self.redo_button)
