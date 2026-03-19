from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass(slots=True)
class ExportColumn:
    name: str
    values: np.ndarray
    formatter: str


@dataclass(slots=True)
class ExportPayload:
    columns: list[ExportColumn]
    delimiter: str = " "
    line_ending: str = "\n"
    encoding: str = "utf-8"
    decimal_separator: str = "."
    metadata: dict[str, str] = field(default_factory=dict)
