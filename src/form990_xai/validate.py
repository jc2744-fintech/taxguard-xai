import json, os

def load_previous(path: str):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"year": None, "metrics": {}}

def run_validations(mapped: dict, prev: dict, cfg: dict):
    flags = []
    # completeness
    required = cfg["validation"]["policies"]["completeness"]["required"]
    for req in required:
        key = _map_req(req)
        if key not in mapped or mapped[key]["value"] is None:
            flags.append({"type": "missing_required", "element": key})
    # non-negative + units present
    for k, v in mapped.items():
        if v["value"] is not None and v["value"] < 0:
            flags.append({"type": "negative_value", "element": k})
        if "unit" not in v:
            flags.append({"type": "missing_unit", "element": k})
    # YoY drift checks
    drift = cfg["validation"]["drift_thresholds"]
    for elem, v in mapped.items():
        prev_metrics = prev.get("metrics", {})
        if elem in prev_metrics and v["value"] is not None:
            pv = prev_metrics[elem]["value"]
            if pv and pv > 0:
                change = abs(v["value"] - pv) / pv
                thr = _drift_threshold(elem, drift)
                if change > thr:
                    flags.append({"type": "yoy_drift", "element": elem, "ratio": change, "threshold": thr})
    return mapped, flags

def _map_req(name):
    m = {"scope1":"Scope1Emissions","scope2":"Scope2Emissions","scope3":"Scope3Emissions",
         "energy":"EnergyConsumption","water":"WaterWithdrawal","waste":"WasteGenerated","diversity":"WomenInLeadership"}
    return m.get(name, name)

def _drift_threshold(elem, drift):
    inv = {"Scope1Emissions":"scope1","EnergyConsumption":"energy","WaterWithdrawal":"water"}
    key = inv.get(elem, None)
    return drift.get(key, 0.3) if key else 0.3
