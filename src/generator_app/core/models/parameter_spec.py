from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


ParameterKind = Literal["int", "float", "bool", "choice", "point_list"]


@dataclass(slots=True)
class ParameterSpec:
    key: str
    label: str
    kind: ParameterKind
    default: Any
    min_value: int | float | None = None
    max_value: int | float | None = None
    step: int | float | None = None
    choices: list[tuple[str, Any]] = field(default_factory=list)
    tooltip: str = ""
    x_label: str = "X"
    y_label: str = "Y"
    min_points: int = 0
    sort_points: bool = True
