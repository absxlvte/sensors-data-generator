from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


ParameterKind = Literal["int", "float", "bool", "choice"]


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
