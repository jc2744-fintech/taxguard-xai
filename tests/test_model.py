from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from form990_xai.model import RiskScreeningModel
from form990_xai.synthetic import generate_synthetic_dataset


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.filings, cls.relations = generate_synthetic_dataset(
            organizations=32,
            years=(2021, 2022, 2023, 2024),
            random_state=7,
        )
        cls.training = cls.filings.loc[cls.filings["tax_year"] < 2024].copy()
        cls.model = RiskScreeningModel().fit(
            cls.training,
            cls.relations.loc[cls.relations["tax_year"] < 2024],
        )

    def test_predict_and_explain(self) -> None:
        scores, explanations = self.model.predict(self.filings.drop(columns="label"), self.relations)
        self.assertEqual(len(scores), len(self.filings))
        self.assertEqual(len(explanations), len(self.filings))
        self.assertTrue(scores["risk_score"].between(0, 1).all())
        self.assertIn("structured_temporal_reasons", explanations[0])
        self.assertEqual(explanations[0]["interpretation"], "screening priority only; not a compliance finding")

    def test_save_and_load(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.joblib"
            self.model.save(path)
            loaded = RiskScreeningModel.load(path)
            scores, _ = loaded.predict(self.filings.head(12).drop(columns="label"), self.relations)
            self.assertEqual(len(scores), 12)
            self.assertTrue(path.with_suffix(".joblib.manifest.json").exists())

    def test_integrity_manifest_detects_artifact_change(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.model.save(Path(directory) / "model.joblib")
            payload = bytearray(path.read_bytes())
            payload[-1] ^= 1
            path.write_bytes(payload)
            with self.assertRaisesRegex(ValueError, "checksum"):
                RiskScreeningModel.load(path)

    def test_evaluate_returns_calibration_metric(self) -> None:
        metrics = self.model.evaluate(self.training, self.relations)
        self.assertIn("brier_score", metrics)
        self.assertGreaterEqual(metrics["brier_score"], 0)
        self.assertGreater(self.model.metadata["stacking"]["completed_folds"], 0)


if __name__ == "__main__":
    unittest.main()
