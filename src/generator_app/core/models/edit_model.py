from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


EditMode = Literal["curve_nodes", "rectangular_segments", "mixed"]


@dataclass(slots=True)
class ControlPoint:
    x: float
    y: float
    locked_x: bool = False
    locked_y: bool = False


@dataclass(slots=True)
class SegmentHandle:
    left_index: int
    right_index: int
    mode: str = "flat"


@dataclass(slots=True)
class EditRules:
    x_min: float | None = None
    x_max: float | None = None
    y_min: float | None = None
    y_max: float | None = None
    allow_add_between_nodes: bool = True


@dataclass(slots=True)
class EditModel:
    control_points: list[ControlPoint] = field(default_factory=list)
    segment_handles: list[SegmentHandle] = field(default_factory=list)
    editable_series_ids: list[str] = field(default_factory=list)
    rules: EditRules = field(default_factory=EditRules)


@dataclass(slots=True)
class EditProfile:
    mode: EditMode
    allow_drag_points: bool = True
    allow_add_points: bool = True
    allow_drag_segments: bool = False
