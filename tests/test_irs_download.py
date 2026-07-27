from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from form990_xai.irs_download import discover_archive_urls_from_html, safe_extract_zip


class IRSDownloadTests(unittest.TestCase):
    def test_catalog_accepts_only_matching_official_archives(self) -> None:
        html = """
        <a href="https://apps.irs.gov/pub/epostcard/990/xml/2026/2026_TEOS_XML_01A.zip">good</a>
        <a href="https://example.com/xml/2026/2026_TEOS_XML_02A.zip">external</a>
        <a href="https://apps.irs.gov/pub/epostcard/990/xml/2025/2025_TEOS_XML_01A.zip">old</a>
        """
        catalog = discover_archive_urls_from_html(html, 2026)
        self.assertEqual(len(catalog), 1)
        self.assertEqual(catalog[0].period, "01A")

    def test_safe_extract_blocks_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "unsafe.zip"
            with zipfile.ZipFile(archive, "w") as handle:
                handle.writestr("../escaped.xml", "<Return/>")
            with self.assertRaisesRegex(ValueError, "unsafe archive member"):
                safe_extract_zip(archive, Path(directory) / "output")

    def test_safe_extract_enforces_uncompressed_limit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "large.zip"
            with zipfile.ZipFile(archive, "w") as handle:
                handle.writestr("return.xml", "x" * 100)
            with self.assertRaisesRegex(ValueError, "uncompressed-size limit"):
                safe_extract_zip(archive, Path(directory) / "output", max_uncompressed_bytes=10)


if __name__ == "__main__":
    unittest.main()
