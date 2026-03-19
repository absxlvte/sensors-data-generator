from __future__ import annotations

import numpy as np


def build_curve_from_control_points(
    control_x: np.ndarray,
    control_y: np.ndarray,
    target_x: np.ndarray,
) -> np.ndarray:
    """
    Temporary placeholder.

    Replace this adapter with the project's real PCHIP interpolation implementation.
    """
    return np.interp(target_x, control_x, control_y)
