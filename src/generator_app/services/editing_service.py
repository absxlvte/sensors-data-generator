from __future__ import annotations

from generator_app.app.task_registry import TaskRegistry
from generator_app.core.models.dataset import GeneratedDataset
from generator_app.core.models.edit_actions import (
    AddPointAction,
    EditAction,
    MovePointAction,
    MoveSegmentAction,
    RemovePointAction,
)


class EditingService:
    def __init__(self, registry: TaskRegistry) -> None:
        self._registry = registry

    def apply_edit(
        self,
        task_id: str,
        dataset: GeneratedDataset,
        action: EditAction,
        params: dict[str, object],
    ) -> GeneratedDataset:
        task = self._registry.get(task_id)
        return task.apply_edit(dataset, action, params)

    def reverse_action(self, action: EditAction) -> EditAction:
        if isinstance(action, MovePointAction):
            return MovePointAction(
                point_index=action.point_index,
                old_x=action.new_x,
                old_y=action.new_y,
                new_x=action.old_x,
                new_y=action.old_y,
            )
        if isinstance(action, AddPointAction):
            return RemovePointAction(
                point_index=action.insert_index,
                x=action.x,
                y=action.y,
            )
        if isinstance(action, RemovePointAction):
            return AddPointAction(
                insert_index=action.point_index,
                x=action.x,
                y=action.y,
            )
        if isinstance(action, MoveSegmentAction):
            return MoveSegmentAction(
                segment_index=action.segment_index,
                delta_x=-action.delta_x,
                delta_y=-action.delta_y,
            )
        msg = f"Unsupported action type: {type(action)!r}"
        raise TypeError(msg)
