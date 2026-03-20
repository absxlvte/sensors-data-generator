from PyQt6.QtWidgets import QApplication

from generator_app.app.settings import AppSettings
from generator_app.app.task_registry import TaskRegistry
from generator_app.services.editing_service import EditingService
from generator_app.services.export_service import ExportService
from generator_app.services.generation_service import GenerationService
from generator_app.services.processing_service import ProcessingService
from generator_app.tasks.blood_sensor.task import BloodSensorTask
from generator_app.tasks.bubble_sensor.task import BubbleSensorTask
from generator_app.tasks.glucose_sensor.task import GlucoseSensorTask
from generator_app.tasks.geiger_sensor.task import GeigerSensorTask
from generator_app.tasks.heart_rate_sensor.task import HeartRateSensorTask
from generator_app.tasks.hydraulic_sensor.task import HydraulicSensorTask
from generator_app.tasks.liquid_level_sensor.task import LiquidLevelSensorTask
from generator_app.tasks.nitrate_sensor.task import NitrateSensorTask
from generator_app.tasks.ph_sensor.task import PHSensorTask
from generator_app.tasks.spo2_sensor.task import SpO2SensorTask
from generator_app.tasks.temperature_sensor.task import TemperatureSensorTask
from generator_app.tasks.test_Sin.task import SineSensorTask
from generator_app.ui.main_window import MainWindow


def bootstrap_application() -> tuple[QApplication, MainWindow]:
    app = QApplication([])
    settings = AppSettings()
    app.setApplicationName(settings.app_name)
    app.setOrganizationName(settings.organization_name)

    registry = TaskRegistry()
    registry.register(TemperatureSensorTask())
    registry.register(HydraulicSensorTask())
    registry.register(BloodSensorTask())
    registry.register(LiquidLevelSensorTask())
    registry.register(GeigerSensorTask())
    registry.register(SpO2SensorTask())
    registry.register(HeartRateSensorTask())
    registry.register(PHSensorTask())
    registry.register(SineSensorTask())
    registry.register(NitrateSensorTask())
    registry.register(GlucoseSensorTask())
    registry.register(BubbleSensorTask())

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
