from pathlib import Path
from jinja2 import Template
from .utils import save_json

MD_TEMPLATE = """
# ESG Summary (Draft)

## Key Metrics (Canonical Units)
{% for k,v in results.items() %}
- **{{k}}**: {{v.value}} {{v.unit}} (sources: {{ v.provenance|length }})
{% endfor %}

## Flags
{% if flags %}
{% for f in flags %}
- **{{f.type}}** — element: {{f.element}}{% if f.type == 'yoy_drift' %} (change={{'{:.1%}'.format(f.ratio)}}, threshold={{'{:.0%}'.format(f.threshold)}}){% endif %}
{% endfor %}
{% else %}
- None
{% endif %}

> Disclaimer: {{ disclaimer }}
"""

def generate_outputs(results: dict, flags: list, out_dir: Path, cfg: dict):
    out_dir.mkdir(parents=True, exist_ok=True)
    disclaimer = "This ESG summary is AI-assisted and must be reviewed by qualified practitioners."
    t = Template(MD_TEMPLATE)
    md = t.render(results=results, flags=flags, disclaimer=disclaimer)
    (out_dir / "esg_summary.md").write_text(md, encoding="utf-8")
    save_json(out_dir / "esg_summary.json", {"results": results, "flags": flags})
    return {"md": str(out_dir / "esg_summary.md"), "json": str(out_dir / "esg_summary.json")}
