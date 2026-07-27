from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from form990_xai.provenance import build_dataset_manifest, dataframe_fingerprint
from form990_xai.quality import audit_filings
from form990_xai.synthetic import generate_synthetic_dataset


class QualityAndProvenanceTests(unittest.TestCase):
    def test_fingerprint_is_independent_of_row_order(self) -> None:
        frame = pd.DataFrame(
            [{"filing_id": "b", "value": 2}, {"filing_id": "a", "value": 1}]
        )
        shuffled = frame.sample(frac=1, random_state=9)
        self.assertEqual(dataframe_fingerprint(frame), dataframe_fingerprint(shuffled))

    def test_quality_audit_has_reconciliation_metadata(self) -> None:
        filings, _ = generate_synthetic_dataset(12, (2022, 2023, 2024), 3)
        audit = audit_filings(filings)
        self.assertEqual(audit.summary["rows_received"], 36)
        self.assertEqual(audit.summary["issue_count"], 0)
        self.assertIn("numeric_field_coverage", audit.summary)

    def test_manifest_records_all_table_fingerprints(self) -> None:
        filings, relations = generate_synthetic_dataset(12, (2022, 2023, 2024), 4)
        manifest = build_dataset_manifest(
            dataset_name="fixture",
            filings=filings,
            relations=relations,
            parser_version="test",
        )
        with tempfile.TemporaryDirectory() as directory:
            path = manifest.write(Path(directory) / "dataset_manifest.json")
            self.assertTrue(path.exists())
        self.assertEqual(set(manifest.fingerprints), {"filings", "relations", "officers"})


if __name__ == "__main__":
    unittest.main()
