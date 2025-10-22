import json

def _load_units(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_candidates(cands: dict, units_path: str):
    units = _load_units(units_path)
    out = {}
    for group, arr in cands.items():
        for c in arr:
            val = c["value"]; unit = (c.get("unit") or "").lower()
            if group in ["scope1","scope2","scope3"]:
                # convert to tCO2e
                if unit in ("kg","kilograms"):
                    val = val / 1000.0
                elif unit in ("t","tonnes"):
                    val = val
                elif unit in ("tons",):
                    val = val * (units["mass"]["tons"]/1000.0)
                canonical = {"value": val, "unit": "tCO2e", "source": c["source"]}
            elif group == "energy":
                if unit == "kwh":
                    val = val / 1000.0
                elif unit == "mwh":
                    val = val
                canonical = {"value": val, "unit": "MWh", "source": c["source"]}
            elif group == "water":
                canonical = {"value": val, "unit": "m3", "source": c["source"]}
            elif group == "waste":
                canonical = {"value": val, "unit": "t", "source": c["source"]}
            elif group == "diversity":
                canonical = {"value": val, "unit": "%", "source": c["source"]}
            else:
                continue
            out.setdefault(group, []).append(canonical)
    return out
