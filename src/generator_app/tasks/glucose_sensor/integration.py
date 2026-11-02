from __future__ import annotations

import numpy as np


def trapezoidal_integral(values: np.ndarray, x_values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    x_values = np.asarray(x_values, dtype=float)
    return float(np.sum((values[:-1] + values[1:]) * np.diff(x_values) / 2.0))
