from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

from form990_xai.model import ModelSettings, RiskScreeningModel
from form990_xai.synthetic import generate_synthetic_dataset


@unittest.skipUnless(importlib.util.find_spec("fastapi"), "optional API dependencies are not installed")
class OptionalAPITests(unittest.TestCase):
    def test_app_verifies_model_and_scores(self) -> None:
        from form990_xai.api import ScoreRequest, create_app

        filings, relations = generate_synthetic_dataset(12, (2021, 2022, 2023), 27)
        model = RiskScreeningModel(ModelSettings(stacking_folds=2)).fit(filings, relations)
        with tempfile.TemporaryDirectory() as directory:
            model_path = model.save(Path(directory) / "model.joblib")
            app = create_app(model_path)
            routes = {route.path: route for route in app.routes}
            self.assertTrue({"/health", "/model", "/score"}.issubset(routes))
            self.assertTrue(routes["/health"].endpoint()["integrity_verified"])

            candidate = filings.tail(2).drop(columns="label").to_dict(orient="records")
            request = ScoreRequest(filings=candidate, relations=[], include_explanations=True)
            response = routes["/score"].endpoint(request)
            self.assertEqual(len(response.scores), 2)
            self.assertEqual(len(response.explanations), 2)


if __name__ == "__main__":
    unittest.main()
