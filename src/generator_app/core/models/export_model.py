from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass(slots=True)
class ExportColumn:
    name: str
    values: np.ndarray
    formatter: str


@dataclass(slots=True)
class ExportFile:
    filename: str
    columns: list[ExportColumn]


@dataclass(slots=True)
class ExportPayload:
    columns: list[ExportColumn] = field(default_factory=list)
    files: list[ExportFile] = field(default_factory=list)
    delimiter: str = " "
    line_ending: str = "\n"
    encoding: str = "utf-8"
    decimal_separator: str = "."
    metadata: dict[str, str] = field(default_factory=dict)
