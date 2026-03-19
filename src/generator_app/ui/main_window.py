from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
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

        self.setWindowTitle(settings.app_name)
        self.resize(1440, 900)
        self._build_ui()
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
        self.generate_button = QPushButton("Сгенерировать случайно", left_panel)
        self.save_button = QPushButton("Сохранить TXT", left_panel)
        self.processed_button = QPushButton("Показать обработанные данные", left_panel)

        left_layout.addWidget(self.task_selector)
        left_layout.addWidget(self.parameter_form)
        left_layout.addWidget(self.toolbar)
        left_layout.addWidget(self.generate_button)
        left_layout.addWidget(self.save_button)
        left_layout.addWidget(self.processed_button)
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
        self.plot_editor.point_moved.connect(self._on_plot_point_moved)

    def _load_first_task(self) -> None:
        tasks = self._registry.all()
        if tasks:
            self._apply_task_to_ui(tasks[0].id)

    def _on_task_changed(self, task_id: str) -> None:
        self._apply_task_to_ui(task_id)

    def _apply_task_to_ui(self, task_id: str) -> None:
        task = self._registry.get(task_id)
        default_params = task.default_parameters()
        self.parameter_form.set_schema(task.parameter_schema(), default_params)
        self._apply_edit_profile(task.edit_profile(default_params))
        self._current_dataset = None
        self._history.clear()
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
            self._export_service.save_txt(Path(target_dir), payload)
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

        self._export_service.save_txt(Path(target_path), payload)
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
        dialog = ProcessedDataDialog(processed_view, self)
        dialog.exec()
