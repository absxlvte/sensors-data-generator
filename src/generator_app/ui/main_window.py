from __future__ import annotations

from pathlib import Path

import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from generator_app.app.settings import AppSettings
from generator_app.app.task_registry import TaskRegistry
from generator_app.core.history.undo_redo import UndoRedoManager
from generator_app.core.models.dataset import GeneratedDataset
from generator_app.services.editing_service import EditingService
from generator_app.services.export_service import ExportService
from generator_app.services.generation_service import GenerationService
from generator_app.services.processing_service import ProcessingService
from generator_app.ui.dialogs.processed_data_dialog import ProcessedDataDialog
from generator_app.ui.widgets.parameter_form import ParameterFormWidget
from generator_app.ui.widgets.plot_editor_widget import PlotEditorWidget
from generator_app.ui.widgets.task_selector import TaskSelectorWidget
from generator_app.ui.widgets.toolbar_widget import ToolbarWidget


class MainWindow(QMainWindow):
    def __init__(
        self,
        registry: TaskRegistry,
        generation_service: GenerationService,
        editing_service: EditingService,
        export_service: ExportService,
        processing_service: ProcessingService,
        settings: AppSettings,
    ) -> None:
        super().__init__()
        self._registry = registry
        self._generation_service = generation_service
        self._editing_service = editing_service
        self._export_service = export_service
        self._processing_service = processing_service
        self._settings = settings

        self._history = UndoRedoManager()
        self._current_dataset: GeneratedDataset | None = None
        self._theme = "dark"

        self.setWindowTitle(settings.app_name)
        self.resize(1440, 900)
        self._build_ui()
        self._apply_theme(self._theme)
        self._load_first_task()

    def _build_ui(self) -> None:
        root = QWidget(self)
        self.setCentralWidget(root)

        layout = QHBoxLayout(root)
        splitter = QSplitter(Qt.Orientation.Horizontal, root)
        layout.addWidget(splitter)

        left_panel = QWidget(splitter)
        left_layout = QVBoxLayout(left_panel)
        self.task_selector = TaskSelectorWidget(self._registry.all(), left_panel)
        self.parameter_form = ParameterFormWidget(left_panel)
        self.toolbar = ToolbarWidget(left_panel)
        self.generate_button = QPushButton("Сгенерировать", left_panel)
        self.save_button = QPushButton("Сохранить TXT", left_panel)
        self.include_time_checkbox = QCheckBox("Добавить время в выходной файл", left_panel)
        self.include_time_checkbox.setChecked(True)
        self.include_time_checkbox.setToolTip(
            "Добавлять столбец времени или номера измерения, в зависимости от задания."
        )
        self.processed_button = QPushButton("Показать обработанные данные", left_panel)
        self.theme_button = QPushButton("", left_panel)
        self.exit_button = QPushButton("Выход", left_panel)

        left_layout.addWidget(self.task_selector)
        left_layout.addWidget(self.parameter_form)
        left_layout.addWidget(self.toolbar)
        left_layout.addWidget(self.generate_button)
        left_layout.addWidget(self.save_button)
        left_layout.addWidget(self.include_time_checkbox)
        left_layout.addWidget(self.processed_button)
        left_layout.addWidget(self.theme_button)
        left_layout.addWidget(self.exit_button)
        left_layout.addStretch(1)

        right_panel = QWidget(splitter)
        right_layout = QVBoxLayout(right_panel)
        self.plot_editor = PlotEditorWidget(right_panel)
        right_layout.addWidget(self.plot_editor)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([380, 1060])

        self.task_selector.task_changed.connect(self._on_task_changed)
        self.generate_button.clicked.connect(self._generate_current_task)
        self.save_button.clicked.connect(self._save_current_dataset)
        self.processed_button.clicked.connect(self._show_processed_view)
        self.theme_button.clicked.connect(self._toggle_theme)
        self.exit_button.clicked.connect(self.close)
        self.toolbar.undo_button.clicked.connect(self._undo_last_edit)
        self.toolbar.redo_button.clicked.connect(self._redo_last_edit)
        self.plot_editor.point_moved.connect(self._on_plot_point_moved)

    def _toggle_theme(self) -> None:
        self._apply_theme("light" if self._theme == "dark" else "dark")

    def _apply_theme(self, theme: str) -> None:
        self._theme = theme
        app = QApplication.instance()
        if app is None:
            return

        if theme == "light":
            pg.setConfigOptions(background="#ECEFF1", foreground="#1F2933")
            app.setStyleSheet(self._light_stylesheet())
            self.theme_button.setText("Темная тема")
        else:
            pg.setConfigOptions(background="#111318", foreground="#E5E7EB")
            app.setStyleSheet(self._dark_stylesheet())
            self.theme_button.setText("Светлая тема")

        self.plot_editor.set_theme(theme)
        if self._current_dataset is not None:
            self.plot_editor.set_dataset(self._current_dataset)

    @staticmethod
    def _light_stylesheet() -> str:
        return """
        QWidget {
            background-color: #E6EAEE;
            color: #1F2933;
        }
        QMainWindow, QDialog {
            background-color: #E6EAEE;
        }
        QPushButton, QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit, QCheckBox, QTableWidget {
            background-color: #F7F9FB;
            color: #1F2933;
            border: 1px solid #B0BEC5;
            border-radius: 6px;
            padding: 6px;
        }
        QPushButton:hover {
            background-color: #FFFFFF;
        }
        QGroupBox {
            border: 1px solid #B0BEC5;
            border-radius: 6px;
            margin-top: 8px;
            padding-top: 8px;
        }
        QHeaderView::section {
            background-color: #CFD8DC;
            color: #1F2933;
            padding: 4px;
            border: 1px solid #B0BEC5;
        }
        """

    @staticmethod
    def _dark_stylesheet() -> str:
        return """
        QWidget {
            background-color: #1A1D24;
            color: #E5E7EB;
        }
        QMainWindow, QDialog {
            background-color: #1A1D24;
        }
        QPushButton, QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit, QCheckBox, QTableWidget {
            background-color: #252A33;
            color: #E5E7EB;
            border: 1px solid #3A414D;
            border-radius: 6px;
            padding: 6px;
        }
        QPushButton:hover {
            background-color: #2F3642;
        }
        QGroupBox {
            border: 1px solid #3A414D;
            border-radius: 6px;
            margin-top: 8px;
            padding-top: 8px;
        }
        QHeaderView::section {
            background-color: #252A33;
            color: #E5E7EB;
            padding: 4px;
            border: 1px solid #3A414D;
        }
        """

    def _load_first_task(self) -> None:
        tasks = self._registry.all()
        if tasks:
            self._apply_task_to_ui(tasks[0].id)

    def _on_task_changed(self, task_id: str) -> None:
        self._apply_task_to_ui(task_id)

    def _apply_task_to_ui(self, task_id: str) -> None:
        task = self._registry.get(task_id)
        self.include_time_checkbox.setEnabled(
            task_id not in {"bubble_sensor", "nitrate_sensor"}
        )
        default_params = task.default_parameters()
        self.parameter_form.set_schema(task.parameter_schema(), default_params)
        self._apply_edit_profile(task.edit_profile(default_params))
        self._current_dataset = None
        self._history.clear()
        self._sync_history_buttons()
        self.plot_editor.set_dataset(None)

    def _apply_edit_profile(self, profile) -> None:
        self.toolbar.move_point_button.setEnabled(profile.allow_drag_points)
        self.toolbar.add_point_button.setEnabled(profile.allow_add_points)
        self.toolbar.move_segment_button.setEnabled(profile.allow_drag_segments)
        has_editing = (
            profile.allow_drag_points
            or profile.allow_add_points
            or profile.allow_drag_segments
        )
        self.toolbar.undo_button.setEnabled(has_editing)
        self.toolbar.redo_button.setEnabled(has_editing)
        self.toolbar.setEnabled(has_editing)
        self._sync_history_buttons()

    def _sync_history_buttons(self) -> None:
        self.toolbar.undo_button.setEnabled(self.toolbar.isEnabled() and self._history.can_undo())
        self.toolbar.redo_button.setEnabled(self.toolbar.isEnabled() and self._history.can_redo())

    def _generate_current_task(self) -> None:
        task_id = self.task_selector.current_task_id()
        params = self.parameter_form.collect_values()
        try:
            dataset = self._generation_service.generate(task_id, params)
        except ValueError as error:
            QMessageBox.warning(self, "Ошибка параметров", str(error))
            return
        self._current_dataset = dataset
        self._history.clear()
        self._sync_history_buttons()
        self.plot_editor.set_dataset(dataset)

    def _on_plot_point_moved(self, action) -> None:
        if self._current_dataset is None:
            return

        task_id = self.task_selector.current_task_id()
        params = self.parameter_form.collect_values()
        try:
            updated_dataset = self._editing_service.apply_edit(
                task_id,
                self._current_dataset,
                action,
                params,
            )
        except ValueError as error:
            QMessageBox.warning(self, "Ошибка редактирования", str(error))
            self.plot_editor.set_dataset(self._current_dataset)
            return

        self._history.push(action)
        self._current_dataset = updated_dataset
        if "control_points" in updated_dataset.meta:
            self.parameter_form.set_value("control_points", updated_dataset.meta["control_points"])
        self._sync_history_buttons()
        self.plot_editor.set_dataset(updated_dataset)

    def _undo_last_edit(self) -> None:
        if self._current_dataset is None:
            return

        action = self._history.pop_undo()
        if action is None:
            self._sync_history_buttons()
            return

        reverse_action = self._editing_service.reverse_action(action)
        task_id = self.task_selector.current_task_id()
        params = self.parameter_form.collect_values()
        try:
            updated_dataset = self._editing_service.apply_edit(
                task_id,
                self._current_dataset,
                reverse_action,
                params,
            )
        except ValueError as error:
            QMessageBox.warning(self, "Ошибка отмены", str(error))
            self._sync_history_buttons()
            return

        self._current_dataset = updated_dataset
        if "control_points" in updated_dataset.meta:
            self.parameter_form.set_value("control_points", updated_dataset.meta["control_points"])
        self._sync_history_buttons()
        self.plot_editor.set_dataset(updated_dataset)

    def _redo_last_edit(self) -> None:
        if self._current_dataset is None:
            return

        action = self._history.pop_redo()
        if action is None:
            self._sync_history_buttons()
            return

        task_id = self.task_selector.current_task_id()
        params = self.parameter_form.collect_values()
        try:
            updated_dataset = self._editing_service.apply_edit(
                task_id,
                self._current_dataset,
                action,
                params,
            )
        except ValueError as error:
            QMessageBox.warning(self, "Ошибка повтора", str(error))
            self._sync_history_buttons()
            return

        self._current_dataset = updated_dataset
        if "control_points" in updated_dataset.meta:
            self.parameter_form.set_value("control_points", updated_dataset.meta["control_points"])
        self._sync_history_buttons()
        self.plot_editor.set_dataset(updated_dataset)

    def _save_current_dataset(self) -> None:
        if self._current_dataset is None:
            QMessageBox.information(self, "Нет данных", "Сначала сгенерируйте данные.")
            return

        task_id = self.task_selector.current_task_id()
        params = self.parameter_form.collect_values()
        task = self._registry.get(task_id)
        payload = task.build_export_payload(self._current_dataset, params)

        if payload.files:
            target_dir = QFileDialog.getExistingDirectory(
                self,
                "Выберите папку для TXT файлов",
                str(self._settings.default_export_dir),
            )
            if not target_dir:
                return
            self._export_service.save_txt(
                Path(target_dir), payload, include_time=self.include_time_checkbox.isChecked()
            )
            QMessageBox.information(self, "Сохранено", "TXT файлы сохранены в выбранную папку.")
            return

        target_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить TXT",
            str(Path(self._settings.default_export_dir) / f"{task_id}.txt"),
            "Text files (*.txt)",
        )
        if not target_path:
            return

        self._export_service.save_txt(
            Path(target_path), payload, include_time=self.include_time_checkbox.isChecked()
        )
        QMessageBox.information(self, "Сохранено", "Файл успешно сохранен.")

    def _show_processed_view(self) -> None:
        if self._current_dataset is None:
            QMessageBox.information(self, "Нет данных", "Сначала сгенерируйте данные.")
            return

        task_id = self.task_selector.current_task_id()
        params = self.parameter_form.collect_values()
        processed_view = self._processing_service.build_processed_view(
            task_id,
            self._current_dataset,
            params,
        )
        if processed_view is None:
            QMessageBox.information(
                self,
                "Нет обработки",
                "Для этого датчика обработанные данные не заданы.",
            )
            return
        dialog = ProcessedDataDialog(processed_view, self, theme=self._theme)
        dialog.exec()
