from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import DataSeries, GeneratedDataset
from generator_app.core.models.edit_model import EditModel


def _load_neurokit2():
    try:
        import neurokit2 as nk  # type: ignore
    except ImportError as error:  # pragma: no cover - depends on local env
        raise ValueError(
            "Для датчика ЧСС требуется библиотека neurokit2. "
            "Обновите окружение командой `python -m pip install -e .`."
        ) from error
    return nk


def _scale_signal(signal: np.ndarray, target_min: float, target_max: float) -> np.ndarray:
    signal = np.asarray(signal, dtype=float)
    current_min = float(np.min(signal))
    current_max = float(np.max(signal))
    if np.isclose(current_max, current_min):
        return np.full_like(signal, (target_min + target_max) / 2.0)
    current_center = (current_max + current_min) / 2.0
    target_center = (target_max + target_min) / 2.0
    current_amplitude = current_max - current_min
    target_amplitude = target_max - target_min
    return (signal - current_center) * (target_amplitude / current_amplitude) + target_center


def generate_heart_rate_dataset(params: dict[str, int | float]) -> GeneratedDataset:
    nk = _load_neurokit2()

    duration = float(params["duration"])
    heart_rate = int(params["heart_rate"])
    noise_level = float(params["noise_level"])
    sampling_rate = int(params["sampling_rate"])

    ecg_signal = nk.ecg_simulate(
        duration=duration,
        heart_rate=heart_rate,
        sampling_rate=sampling_rate,
        noise=noise_level,
        method="simple",
    )
    ecg_signal = np.asarray(ecg_signal, dtype=float)

    cut_index = min(100, max(0, ecg_signal.size - 1))
    ecg_signal = ecg_signal[cut_index:]
    time_axis = np.linspace(0.0, duration, int(duration * sampling_rate), dtype=float)[cut_index:]
    voltage_signal = _scale_signal(ecg_signal, 0.1, 3.0)

    return GeneratedDataset(
        task_id="heart_rate_sensor",
        series=[
            DataSeries(
                id="heart_rate_signal",
                name="ЭКГ-сигнал",
                x=time_axis,
                y=voltage_signal,
                editable=False,
            ),
        ],
        edit_model=EditModel(editable_series_ids=[]),
        meta={
            "time_axis": time_axis,
            "signal": voltage_signal,
            "target_heart_rate": heart_rate,
            "sampling_rate": sampling_rate,
            "duration": duration,
        },
    )
