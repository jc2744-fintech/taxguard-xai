import regex as re
from .utils import load_yaml

def extract_metrics(docs, patterns_path: str):
    cfg = load_yaml(patterns_path)
    pats = cfg["patterns"]
    candidates = {}
    hits = []
    def add(name, value, unit, src):
        candidates.setdefault(name, []).append({"value": value, "unit": unit, "source": src})
    for d in docs:
        txt = d["text"]
        for group, arr in pats.items():
            for p in arr:
                for m in re.finditer(p["regex"], txt):
                    groups = m.groups()
                    # pick first numeric and last textual unit
                    val = None; unit = ""
                    for g in groups:
                        if g is None: 
                            continue
                        g_clean = re.sub(r"[\s,]", "", g)
                        if re.match(r"^\d*\.?\d+$", g_clean):
                            val = float(g_clean); break
                    # last non-numeric as unit
                    for g in reversed(groups):
                        if g and not re.match(r"^\d*\.?\d+$", re.sub(r"[\s,]","", g)):
                            unit = g.lower(); break
                    if val is not None:
                        add(group, val, unit, d["path"])
                        hits.append({"group": group, "pattern": p["name"], "span": m.span(), "source": d["path"]})
    return candidates, hits
