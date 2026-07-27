from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from form990_xai.anomaly import ExplainableAnomalyDetector
from form990_xai.drift import analyze_drift
from form990_xai.evaluation import (
    expected_calibration_error,
    review_budget_metrics,
    rolling_origin_folds,
)
from form990_xai.experiment import run_experiment
from form990_xai.synthetic import generate_synthetic_dataset
from form990_xai.weak_supervision import apply_review_signals


class ResearchWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.filings, cls.relations = generate_synthetic_dataset(
            18, (2021, 2022, 2023, 2024), 19
        )

    def test_weak_supervision_is_traceable(self) -> None:
        result = apply_review_signals(self.filings, self.relations)
        self.assertEqual(len(result.labels), len(self.filings))
        self.assertEqual(result.report["labeling_functions"], 11)
        decoded = json.loads(result.labels.iloc[0]["signal_explanations_json"])
        self.assertIsInstance(decoded, list)

    def test_anomaly_detector_returns_reasons(self) -> None:
        detector = ExplainableAnomalyDetector().fit(
            self.filings.drop(columns="label"), self.relations
        )
        scores = detector.score(self.filings.head(5).drop(columns="label"), self.relations)
        self.assertEqual(len(scores), 5)
        self.assertTrue(scores["anomaly_percentile"].between(0, 1).all())
        self.assertIsInstance(json.loads(scores.iloc[0]["anomaly_reasons_json"]), list)

    def test_capacity_and_calibration_metrics(self) -> None:
        budget = review_budget_metrics([0, 1, 0, 1], [0.1, 0.9, 0.2, 0.8], 0.5)
        self.assertEqual(budget["review_count"], 2)
        self.assertEqual(budget["positives_found"], 2)
        self.assertAlmostEqual(expected_calibration_error([0, 1], [0.1, 0.9], bins=2), 0.1)

    def test_rolling_folds_have_no_future_years(self) -> None:
        folds = rolling_origin_folds(self.filings, min_train_years=2)
        self.assertEqual(folds[0].test_year, 2023)
        self.assertLess(max(folds[0].train_years), folds[0].test_year)

    def test_drift_report_compares_latest_year_to_history(self) -> None:
        reference = self.filings.loc[self.filings["tax_year"] < 2024]
        candidate = self.filings.loc[self.filings["tax_year"] == 2024]
        reference_relations = self.relations.loc[self.relations["tax_year"] < 2024]
        candidate_relations = self.relations.loc[self.relations["tax_year"] == 2024]
        report = analyze_drift(reference, candidate, reference_relations, candidate_relations)
        self.assertGreater(len(report.feature_metrics), 20)
        self.assertEqual(report.summary["candidate_tax_years"], [2024])
        self.assertIn("population_stability_index", report.feature_metrics)

    def test_configured_experiment_writes_reproducibility_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = {
                "name": "unit-experiment",
                "random_state": 5,
                "data": {
                    "kind": "synthetic",
                    "organizations": 16,
                    "years": [2021, 2022, 2023, 2024],
                    "random_state": 5,
                },
                "model": {"stacking_folds": 2, "max_text_features": 200},
                "evaluation": {"min_train_years": 2, "review_budget": 0.2},
                "output_dir": "runs",
            }
            config_path = root / "experiment.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            manifest = run_experiment(config_path)
            outputs = manifest["outputs"]
            for key in [
                "run_manifest",
                "dataset_manifest",
                "backtest_report",
                "drift_summary",
                "html_report",
            ]:
                self.assertTrue(Path(outputs[key]).exists(), key)


if __name__ == "__main__":
    unittest.main()
