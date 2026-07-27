from __future__ import annotations

import numpy as np

from form990_xai.deep.explainability import aggregate_token_attributions, top_numeric_attributions


def test_attribution_helpers_preserve_signs():
    ranked = top_numeric_attributions(["a", "b"], np.array([1, 2]), np.array([-0.2, 0.9]))
    assert ranked[0].feature == "b"
    assert ranked[1].attribution < 0
    tokens = aggregate_token_attributions(["<s>", "revenue", "assets"], np.array([10, -2, 1]))
    assert tokens[0].feature == "revenue"
