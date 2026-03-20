from __future__ import annotations

from generator_app.core.models.dataset import GeneratedDataset
from generator_app.core.models.edit_actions import EditAction


def apply_edit_to_dataset(
    dataset: GeneratedDataset,
    action: EditAction,
    params: dict[str, int | float],
) -> GeneratedDataset:
    return dataset
