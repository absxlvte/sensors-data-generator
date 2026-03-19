from __future__ import annotations

from typing import Any

from generator_app.app.task_registry import TaskRegistry
from generator_app.core.models.dataset import GeneratedDataset


class GenerationService:
    def __init__(self, registry: TaskRegistry) -> None:
        self._registry = registry

    def generate(self, task_id: str, params: dict[str, Any]) -> GeneratedDataset:
        task = self._registry.get(task_id)
        validation = task.validate_parameters(params)
        if not validation.is_valid:
            raise ValueError("\n".join(validation.errors))
        return task.generate_random(params)
