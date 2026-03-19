from PyQt6.QtWidgets import QApplication

from generator_app.app.settings import AppSettings
from generator_app.app.task_registry import TaskRegistry
from generator_app.services.editing_service import EditingService
from generator_app.services.export_service import ExportService
from generator_app.services.generation_service import GenerationService
from generator_app.services.processing_service import ProcessingService
from generator_app.tasks.temperature_demo.task import TemperatureDemoTask
from generator_app.tasks.test_Sin.task import SineSensorTask
from generator_app.ui.main_window import MainWindow


def bootstrap_application() -> tuple[QApplication, MainWindow]:
    app = QApplication([])
    settings = AppSettings()
    app.setApplicationName(settings.app_name)
    app.setOrganizationName(settings.organization_name)

    registry = TaskRegistry()
    registry.register(TemperatureDemoTask())
    registry.register(SineSensorTask())

    generation_service = GenerationService(registry)
    editing_service = EditingService(registry)
    export_service = ExportService()
    processing_service = ProcessingService(registry)

    window = MainWindow(
        registry=registry,
        generation_service=generation_service,
        editing_service=editing_service,
        export_service=export_service,
        processing_service=processing_service,
        settings=settings,
    )
    return app, window
