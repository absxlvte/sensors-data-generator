from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset, ProcessedCurve, ProcessedView


def _load_neurokit2():
    try:
        import neurokit2 as nk  # type: ignore
    except ImportError as error:  # pragma: no cover - depends on local env
        raise ValueError(
            "Для датчика ЧСС требуется библиотека neurokit2. "
            "Обновите окружение командой `python -m pip install -e .`."
        ) from error
    return nk


def _estimate_heart_rate(signal: np.ndarray, sampling_rate: int) -> float:
    nk = _load_neurokit2()
    if signal.size == 0:
        return 0.0
    _, info = nk.ecg_peaks(signal, sampling_rate=sampling_rate)
    peak_indices = np.asarray(info.get("ECG_R_Peaks", []), dtype=int)
    if peak_indices.size < 2:
        return 0.0
    rr_intervals = np.diff(peak_indices) / float(sampling_rate)
    bpm_values = 60.0 / rr_intervals
    return float(np.mean(bpm_values))


def build_processed_view(dataset: GeneratedDataset) -> ProcessedView:
    time_axis = np.asarray(dataset.meta.get("time_axis", []), dtype=float)
    signal = np.asarray(dataset.meta.get("signal", []), dtype=float)
    sampling_rate = int(dataset.meta.get("sampling_rate", 1000))
    target_heart_rate = float(dataset.meta.get("target_heart_rate", 0.0))

    estimated_bpm = _estimate_heart_rate(signal, sampling_rate)
    target_line = np.full_like(time_axis, target_heart_rate, dtype=float)
    estimated_line = np.full_like(time_axis, estimated_bpm, dtype=float)

    return ProcessedView(
        title="Обработка ЧСС",
        curves=[
            ProcessedCurve(
                name="Заданная ЧСС",
                x=time_axis,
                y=target_line,
            ),
            ProcessedCurve(
                name="Рассчитанная ЧСС",
                x=time_axis,
                y=estimated_line,
            ),
        ],
    )
