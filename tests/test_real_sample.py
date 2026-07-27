from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from form990_xai.real_demo import run_real_data_demo
from form990_xai.schema import validate_filings, validate_relations


def test_checked_in_real_snapshot_and_manifest():
    filings = pd.read_csv("data/real_sample/filings.csv", dtype={"ein": str})
    relations = pd.read_csv("data/real_sample/relations.csv", dtype={"source_ein": str, "target_ein": str})
    validated = validate_filings(filings)
    validate_relations(relations)
    manifest = json.loads(Path("data/real_sample/manifest.json").read_text())
    assert len(validated) == 15
    assert validated["ein"].nunique() == 3
    assert manifest["rows"] == 15
    assert validated.loc[validated["filing_id"].eq("910564748-2024"), "total_revenue"].iloc[0] == 2659433037
    assert "label" not in filings.columns


def test_real_demo_produces_label_free_review_artifacts(tmp_path: Path):
    summary = run_real_data_demo(
        "data/real_sample/filings.csv",
        tmp_path,
        relations_path="data/real_sample/relations.csv",
    )
    assert summary["rows"] == 15
    assert "not reported" in summary["supervised_metrics"]
    assert (tmp_path / "review_bundle" / "review_queue.html").exists()
    assert (tmp_path / "quality" / "quality_summary.json").exists()
