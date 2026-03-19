from __future__ import annotations

from pathlib import Path

from generator_app.core.models.export_model import ExportPayload


class ExportService:
    def save_txt(self, path: Path, payload: ExportPayload) -> None:
        if payload.files:
            path.mkdir(parents=True, exist_ok=True)
            for export_file in payload.files:
                self._write_single_file(path / export_file.filename, ExportPayload(
                    columns=export_file.columns,
                    delimiter=payload.delimiter,
                    line_ending=payload.line_ending,
                    encoding=payload.encoding,
                    decimal_separator=payload.decimal_separator,
                    metadata=dict(payload.metadata),
                ))
            return

        self._write_single_file(path, payload)

    def _write_single_file(self, path: Path, payload: ExportPayload) -> None:
        rows: list[str] = []
        column_count = len(payload.columns)
        if column_count == 0:
            raise ValueError("Export payload has no columns.")

        row_count = len(payload.columns[0].values)
        for row_index in range(row_count):
            parts: list[str] = []
            for column in payload.columns:
                raw_value = column.values[row_index]
                formatted = format(raw_value, column.formatter)
                if payload.decimal_separator != ".":
                    formatted = formatted.replace(".", payload.decimal_separator)
                parts.append(formatted)
            rows.append(payload.delimiter.join(parts))
        path.write_text(payload.line_ending.join(rows), encoding=payload.encoding)
