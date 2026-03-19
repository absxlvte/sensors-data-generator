from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MovePointAction:
    point_index: int
    old_x: float
    old_y: float
    new_x: float
    new_y: float


@dataclass(slots=True)
class AddPointAction:
    insert_index: int
    x: float
    y: float


@dataclass(slots=True)
class RemovePointAction:
    point_index: int
    x: float
    y: float


@dataclass(slots=True)
class MoveSegmentAction:
    segment_index: int
    delta_x: float
    delta_y: float


EditAction = MovePointAction | AddPointAction | RemovePointAction | MoveSegmentAction
