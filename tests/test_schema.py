from __future__ import annotations

import unittest

import pandas as pd

from form990_xai.schema import normalize_ein, validate_filings, validate_relations


class SchemaTests(unittest.TestCase):
    def test_normalize_ein_preserves_nine_digits(self) -> None:
        self.assertEqual(normalize_ein("01-2345678"), "012345678")

    def test_validate_filings_adds_optional_columns(self) -> None:
        frame = pd.DataFrame([{"filing_id": "a", "ein": "01-2345678", "tax_year": 2025}])
        result = validate_filings(frame)
        self.assertEqual(result.loc[0, "ein"], "012345678")
        self.assertIn("narrative", result)

    def test_training_requires_two_classes(self) -> None:
        frame = pd.DataFrame(
            [
                {"filing_id": "a", "ein": "1", "tax_year": 2024, "label": 0},
                {"filing_id": "b", "ein": "2", "tax_year": 2024, "label": 0},
            ]
        )
        with self.assertRaisesRegex(ValueError, "both label classes"):
            validate_filings(frame, require_label=True)

    def test_empty_relations_are_supported(self) -> None:
        result = validate_relations(None)
        self.assertTrue(result.empty)
        self.assertIn("source_ein", result)


if __name__ == "__main__":
    unittest.main()
