from __future__ import annotations

import unittest

from form990_xai.features import GRAPH_FEATURES, STRUCTURED_TEMPORAL_FEATURES, build_model_frame
from form990_xai.synthetic import generate_synthetic_dataset


class FeatureTests(unittest.TestCase):
    def test_all_branches_are_finite(self) -> None:
        filings, relations = generate_synthetic_dataset(organizations=16, years=(2022, 2023, 2024))
        frame = build_model_frame(filings, relations)
        self.assertEqual(len(frame), len(filings))
        self.assertFalse(frame[STRUCTURED_TEMPORAL_FEATURES + GRAPH_FEATURES].isna().any().any())

    def test_temporal_change_uses_prior_year(self) -> None:
        filings, relations = generate_synthetic_dataset(organizations=12, years=(2022, 2023, 2024))
        frame = build_model_frame(filings, relations).sort_values(["ein", "tax_year"])
        first_year = frame.groupby("ein").head(1)
        self.assertTrue((first_year["revenue_change"] == 0).all())


if __name__ == "__main__":
    unittest.main()
