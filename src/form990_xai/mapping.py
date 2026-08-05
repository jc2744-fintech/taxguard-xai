import json

def map_to_taxonomy(canonical: dict, taxonomy_path: str):
    with open(taxonomy_path, "r", encoding="utf-8") as f:
        tax = json.load(f)
    mapping = {
        "scope1": "Scope1Emissions",
        "scope2": "Scope2Emissions",
        "scope3": "Scope3Emissions",
        "energy": "EnergyConsumption",
        "water": "WaterWithdrawal",
        "waste": "WasteGenerated",
        "diversity": "WomenInLeadership"
    }
    results = {}
    for k, v in canonical.items():
        key = mapping.get(k)
        if not key: 
            continue
        values = sorted([x["value"] for x in v])
        val = values[len(values)//2] if values else None
        results[key] = {"value": val, "unit": tax["elements"][key]["unit"], "provenance": [x["source"] for x in v]}
    return results
