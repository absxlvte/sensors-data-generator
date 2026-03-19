from __future__ import annotations

from dataclasses import dataclass, field

from generator_app.core.models.edit_actions import EditAction


@dataclass(slots=True)
class UndoRedoManager:
    undo_stack: list[EditAction] = field(default_factory=list)
    redo_stack: list[EditAction] = field(default_factory=list)

    def push(self, action: EditAction) -> None:
        self.undo_stack.append(action)
        self.redo_stack.clear()

    def can_undo(self) -> bool:
        return bool(self.undo_stack)

    def can_redo(self) -> bool:
        return bool(self.redo_stack)

    def pop_undo(self) -> EditAction | None:
        if not self.undo_stack:
            return None
        action = self.undo_stack.pop()
        self.redo_stack.append(action)
        return action

    def pop_redo(self) -> EditAction | None:
        if not self.redo_stack:
            return None
        action = self.redo_stack.pop()
        self.undo_stack.append(action)
        return action

    def clear(self) -> None:
        self.undo_stack.clear()
        self.redo_stack.clear()
