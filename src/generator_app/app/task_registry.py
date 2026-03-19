from __future__ import annotations

from dataclasses import dataclass, field

from generator_app.core.interfaces.sensor_task import SensorTask


@dataclass(slots=True)
class TaskRegistry:
    tasks: dict[str, SensorTask] = field(default_factory=dict)

    def register(self, task: SensorTask) -> None:
        if task.id in self.tasks:
            msg = f"Task with id '{task.id}' is already registered."
            raise ValueError(msg)
        self.tasks[task.id] = task

    def all(self) -> list[SensorTask]:
        return sorted(self.tasks.values(), key=lambda item: item.display_name)

    def get(self, task_id: str) -> SensorTask:
        try:
            return self.tasks[task_id]
        except KeyError as error:
            msg = f"Task with id '{task_id}' is not registered."
            raise LookupError(msg) from error
