from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


ToolName = Literal["move_point", "add_point", "move_segment"]


@dataclass(slots=True)
class ToolState:
    active_tool: ToolName = "move_point"
