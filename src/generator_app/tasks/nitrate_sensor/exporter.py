from __future__ import annotations

import numpy as np

from generator_app.core.models.dataset import GeneratedDataset
from generator_app.core.models.export_model import ExportColumn, ExportFile, ExportPayload


FILE_NAMES: dict[str, str] = {
    "Tomatoes": "tomatoes.txt",
    "Spinach": "spinach.txt",
    "Beet": "beet.txt",
    "Cabbage": "cabbage.txt",
    "Carrot": "carrot.txt",
    "Potato": "potato.txt",
    "Cucumbers": "cucumbers.txt",
}


def build_export_payload(dataset: GeneratedDataset) -> ExportPayload:
    export_order = dataset.meta.get("export_order", [])
    files: list[ExportFile] = []
    for product in export_order:
        series = next(item for item in dataset.series if item.id == product)
        files.append(
            ExportFile(
                filename=FILE_NAMES[product],
                columns=[
                    ExportColumn(name="time", values=np.asarray(series.x), formatter=".0f"),
                    ExportColumn(name="Z", values=np.asarray(series.y), formatter=".0f"),
                ],
            )
        )

    return ExportPayload(
        files=files,
        delimiter=" ",
        line_ending="\n",
        encoding="utf-8",
    )
