from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from generator_app.core.models.edit_model import EditModel


@dataclass(slots=True)
class DataSeries:
    id: str
    name: str
    x: np.ndarray
    y: np.ndarray
    editable: bool
    visible: bool = True
    unit: str | None = None
    role: str = "raw"


@dataclass(slots=True)
class GeneratedDataset:
    task_id: str
    series: list[DataSeries]
    edit_model: EditModel
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProcessedCurve:
    name: str
    x: np.ndarray
    y: np.ndarray
    color: str | None = None
    line_style: str = "solid"


@dataclass(slots=True)
class ProcessedView:
    title: str
    curves: list[ProcessedCurve]
