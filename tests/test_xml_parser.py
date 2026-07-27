from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from form990_xai.xml_parser import (
    parse_filing_xml,
    parse_return_xml,
    parse_xml_archive,
    parse_xml_directory,
)

FIXTURE = Path(__file__).parent / "fixtures" / "minimal_990.xml"
REALISTIC_FIXTURE = Path(__file__).parent / "fixtures" / "realistic_990.xml"


class XmlParserTests(unittest.TestCase):
    def test_parse_minimal_filing(self) -> None:
        record = parse_filing_xml(FIXTURE)
        self.assertEqual(record["ein"], "012345678")
        self.assertEqual(record["tax_year"], 2025)
        self.assertEqual(record["filing_id"], "TEST-OBJECT-1")
        self.assertEqual(record["total_revenue"], 1_000_000.0)
        self.assertEqual(record["conflict_policy"], 1)
        self.assertEqual(record["material_diversion"], 0)
        self.assertIn("educational services", record["narrative"])

    def test_parse_directory(self) -> None:
        frame = parse_xml_directory(FIXTURE.parent)
        self.assertGreaterEqual(len(frame), 1)

    def test_extracts_heterogeneous_entities_without_names(self) -> None:
        result = parse_return_xml(REALISTIC_FIXTURE, entity_salt="unit-test-study-salt")
        self.assertEqual(result.filing["filing_type"], "990")
        self.assertEqual(result.filing["net_assets"], 3_500_000.0)
        self.assertEqual(len(result.officers), 1)
        self.assertEqual(len(result.relations), 2)
        person = result.officers[0]
        self.assertTrue(str(person["person_id"]).startswith("person:"))
        self.assertNotIn("Alex", str(person))
        relation_types = {relation["relation_type"] for relation in result.relations}
        self.assertEqual(relation_types, {"officer", "related_tax_exempt_organization"})

    def test_streams_zip_and_skips_unsafe_member(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "returns.zip"
            with zipfile.ZipFile(archive, "w") as handle:
                handle.write(REALISTIC_FIXTURE, "safe/return.xml")
                handle.writestr("../unsafe.xml", b"<Return/>")
            bundle = parse_xml_archive(archive, entity_salt="unit-test-study-salt")
            self.assertEqual(len(bundle.filings), 1)
            self.assertEqual(bundle.report["failed_returns"], 1)
            self.assertIn("unsafe archive member", bundle.report["errors"][0])

    def test_zip_parser_skips_oversized_member(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "mixed.zip"
            with zipfile.ZipFile(archive, "w") as handle:
                handle.write(REALISTIC_FIXTURE, "safe.xml")
                handle.writestr("oversized.xml", b"x" * (REALISTIC_FIXTURE.stat().st_size + 1_000))
            bundle = parse_xml_archive(
                archive,
                entity_salt="unit-test-study-salt",
                max_member_bytes=REALISTIC_FIXTURE.stat().st_size + 1,
            )
            self.assertEqual(len(bundle.filings), 1)
            self.assertIn("oversized archive member", bundle.report["errors"][0])


if __name__ == "__main__":
    unittest.main()
