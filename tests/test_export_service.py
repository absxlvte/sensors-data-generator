from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import numpy as np

from generator_app.core.models.export_model import ExportColumn, ExportFile, ExportPayload
from generator_app.services.export_service import ExportService


class ExportServiceTests(unittest.TestCase):
    def test_optional_time_single_and_multiple_files(self):
        for time_format in (".0f", ".6f"):
            for multiple in (False, True):
                with self.subTest(time_format=time_format, multiple=multiple):
                    columns = [
                        ExportColumn("time", np.array([0, 1]), time_format),
                        ExportColumn("Z", np.array([12, 34]), ".0f"),
                        ExportColumn("Tsend", np.array([0.25, 0.5]), ".6f"),
                    ]
                    payload = ExportPayload(columns=columns) if not multiple else ExportPayload(
                        files=[ExportFile("beet.txt", columns), ExportFile("carrot.txt", columns)]
                    )
                    with TemporaryDirectory() as directory:
                        target = Path(directory) if multiple else Path(directory) / "data.txt"
                        paths = [target / f.filename for f in payload.files] if multiple else [target]
                        service = ExportService()
                        service.save_txt(target, payload, include_time=False)
                        for path in paths:
                            self.assertEqual(path.read_text(), "12 0.250000\n34 0.500000")
                        service.save_txt(target, payload)
                        expected = (
                            f"{format(0, time_format)} 12 0.250000\n"
                            f"{format(1, time_format)} 34 0.500000"
                        )
                        for path in paths:
                            self.assertEqual(path.read_text(), expected)
                        self.assertEqual(len(columns), 3)

    def test_payload_without_time_keeps_all_columns(self):
        payload = ExportPayload(columns=[ExportColumn("Z", np.array([12]), ".0f")])
        with TemporaryDirectory() as directory:
            path = Path(directory) / "data.txt"
            ExportService().save_txt(path, payload, include_time=False)
            self.assertEqual(path.read_text(), "12")
