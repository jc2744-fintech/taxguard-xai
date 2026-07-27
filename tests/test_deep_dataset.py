from __future__ import annotations

import pandas as pd

from form990_xai.deep.dataset import build_graph_arrays, build_temporal_arrays, build_text_records


def test_deep_dataset_builders_without_torch():
    filings = pd.read_csv("data/real_sample/filings.csv", dtype={"ein": str})
    relations = pd.read_csv("data/real_sample/relations.csv", dtype={"source_ein": str, "target_ein": str})
    temporal = build_temporal_arrays(filings, relations, sequence_length=4)
    graph = build_graph_arrays(filings, relations)
    text = build_text_records(filings)
    assert temporal.sequences.shape[0] == len(filings)
    assert temporal.sequences.shape[1] == 4
    assert graph.node_features.shape[0] == len(filings)
    assert graph.edge_index.shape[0] == 2
    assert text["text"].str.len().gt(10).all()
