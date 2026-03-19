from __future__ import annotations

from typing import Any, Protocol

from generator_app.core.models.dataset import GeneratedDataset, ProcessedView
from generator_app.core.models.edit_actions import EditAction
from generator_app.core.models.edit_model import EditProfile
from generator_app.core.models.export_model import ExportPayload
from generator_app.core.models.parameter_spec import ParameterSpec
from generator_app.core.validation.validation_result import ValidationResult


class SensorTask(Protocol):
    id: str
    display_name: str

    def parameter_schema(self) -> list[ParameterSpec]:
        ...

    def default_parameters(self) -> dict[str, Any]:
        ...

    def validate_parameters(self, params: dict[str, Any]) -> ValidationResult:
        ...

    def generate_random(self, params: dict[str, Any]) -> GeneratedDataset:
        ...

    def edit_profile(self, params: dict[str, Any]) -> EditProfile:
        ...

    def apply_edit(
        self,
        dataset: GeneratedDataset,
        action: EditAction,
        params: dict[str, Any],
    ) -> GeneratedDataset:
        ...

    def build_export_payload(
        self,
        dataset: GeneratedDataset,
        params: dict[str, Any],
    ) -> ExportPayload:
        ...

    def build_processed_view(
        self,
        dataset: GeneratedDataset,
        params: dict[str, Any],
    ) -> ProcessedView | None:
        ...
