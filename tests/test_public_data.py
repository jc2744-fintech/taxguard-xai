from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from form990_xai.public_data import fetch_json, propublica_payload_to_filings


class FakeResponse:
    headers = {"Content-Length": "100"}
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, _limit):
        return json.dumps({"organization": {"ein": 123456789, "name": "Example", "state": "WA", "ntee_code": "E20"}, "filings_with_data": [{"ein": 123456789, "tax_prd": 202412, "tax_prd_yr": 2024, "formtype": 0, "totrevenue": 1000, "totfuncexpns": 900, "totassetsend": 5000, "totliabend": 1000, "netassetsend": 4000}]}).encode()


def test_fetch_json_caches_and_hashes(tmp_path: Path):
    destination = tmp_path / "response.json"
    with patch("urllib.request.urlopen", return_value=FakeResponse()):
        payload, metadata = fetch_json("https://example.test/data", cache_path=destination)
    assert payload["organization"]["name"] == "Example"
    assert destination.exists()
    assert len(metadata.sha256) == 64
    cached, cached_metadata = fetch_json("https://example.test/data", cache_path=destination)
    assert cached == payload
    assert cached_metadata.status == "cache_hit"


def test_normalizes_propublica_payload():
    payload = {"organization": {"ein": 123456789, "name": "Example", "state": "WA", "ntee_code": "E20"}, "filings_with_data": [{"ein": 123456789, "tax_prd": 202412, "tax_prd_yr": 2024, "formtype": 0, "totrevenue": 1000, "totfuncexpns": 900, "totassetsend": 5000, "totliabend": 1000, "netassetsend": 4000}]}
    frame = propublica_payload_to_filings(payload)
    assert len(frame) == 1
    assert frame.loc[0, "ein"] == "123456789"
    assert frame.loc[0, "total_revenue"] == 1000
    assert frame.loc[0, "filing_type"] == "990"
