from __future__ import annotations

import numpy as np


def _pchip_slopes(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    count = len(x)
    h = np.diff(x)
    delta = np.diff(y) / h
    slopes = np.zeros(count, dtype=float)

    if count == 2:
        slopes[:] = delta[0]
        return slopes

    for index in range(1, count - 1):
        if delta[index - 1] * delta[index] <= 0:
            slopes[index] = 0.0
        else:
            h1, h2 = h[index - 1], h[index]
            delta1, delta2 = delta[index - 1], delta[index]
            w1 = 2 * h2 + h1
            w2 = h2 + 2 * h1
            slopes[index] = (w1 + w2) / ((w1 / delta1) + (w2 / delta2))

    slopes[0] = ((2 * h[0] + h[1]) * delta[0] - h[0] * delta[1]) / (h[0] + h[1])
    if np.sign(slopes[0]) != np.sign(delta[0]):
        slopes[0] = 0.0
    elif np.sign(delta[0]) != np.sign(delta[1]) and abs(slopes[0]) > abs(3 * delta[0]):
        slopes[0] = 3 * delta[0]

    slopes[-1] = ((2 * h[-1] + h[-2]) * delta[-1] - h[-1] * delta[-2]) / (h[-1] + h[-2])
    if np.sign(slopes[-1]) != np.sign(delta[-1]):
        slopes[-1] = 0.0
    elif np.sign(delta[-1]) != np.sign(delta[-2]) and abs(slopes[-1]) > abs(3 * delta[-1]):
        slopes[-1] = 3 * delta[-1]

    return slopes


def build_curve_from_control_points(
    control_x: np.ndarray,
    control_y: np.ndarray,
    target_x: np.ndarray,
) -> np.ndarray:
    control_x = np.asarray(control_x, dtype=float)
    control_y = np.asarray(control_y, dtype=float)
    target_x = np.asarray(target_x, dtype=float)

    if np.any(np.diff(control_x) <= 0):
        raise ValueError("control_x must be strictly increasing.")

    slopes = _pchip_slopes(control_x, control_y)
    indices = np.searchsorted(control_x, target_x) - 1
    indices = np.clip(indices, 0, len(control_x) - 2)

    h = control_x[1:] - control_x[:-1]
    delta = (control_y[1:] - control_y[:-1]) / h

    interval_h = h[indices]
    local_x = target_x - control_x[indices]

    c0 = control_y[indices]
    c1 = slopes[indices]
    c2 = (3 * delta[indices] - 2 * slopes[indices] - slopes[indices + 1]) / interval_h
    c3 = (slopes[indices] + slopes[indices + 1] - 2 * delta[indices]) / (interval_h**2)

    return c0 + c1 * local_x + c2 * local_x**2 + c3 * local_x**3
