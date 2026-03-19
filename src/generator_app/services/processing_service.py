from __future__ import annotations

from generator_app.app.task_registry import TaskRegistry
from generator_app.core.models.dataset import GeneratedDataset, ProcessedView


class ProcessingService:
    def __init__(self, registry: TaskRegistry) -> None:
        self._registry = registry

    def build_processed_view(
        self,
        task_id: str,
        dataset: GeneratedDataset,
        params: dict[str, object],
    ) -> ProcessedView | None:
        task = self._registry.get(task_id)
        return task.build_processed_view(dataset, params)
