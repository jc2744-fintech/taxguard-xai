from __future__ import annotations

import json
import pandas as pd

from form990_xai.peer_graph import build_analytical_graph


def test_peer_graph_is_explicitly_derived():
    filings = pd.read_csv("data/real_sample/filings.csv", dtype={"ein": str})
    graph = build_analytical_graph(filings)
    assert len(graph) > 0
    assert {"derived_temporal_predecessor", "derived_peer_similarity"}.issubset(set(graph["relation_type"]))
    metadata = [json.loads(value) for value in graph["metadata_json"]]
    assert all(item.get("derived") is True for item in metadata)
    assert not graph["relation_type"].isin(["related_organization", "shared_officer"]).any()
