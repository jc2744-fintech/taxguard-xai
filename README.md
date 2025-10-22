# ESGx-DisclosureAI

**Short description**: End-to-end framework for **AI-assisted ESG reporting** — document ingestion → **metric extraction** → **taxonomy mapping** (GRI/SASB-like) → **validation & assurance** → **report generation** with audit trails. Offline-friendly stubs; plug in your LLMs later.

## Highlights
- PDF/HTML/text ingestion stubs with content normalization
- Pattern- and template-based **metric extraction** for Scope 1/2/3, energy, water, waste, diversity
- Unit normalization (kg↔t, kWh↔MWh), boundary checks, double-count detection
- **Taxonomy mapping** to a minimal ESG schema inspired by GRI/SASB
- Policy-aware validation: disclosure completeness, consistency, year-over-year drift
- Report generator: Markdown + JSON summaries; provenance & audit logs
- Reproducible experiments, tests, and CI

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run a demo with toy reports (no external LLMs required)
python -m esgx.cli demo --inputs data/sample/reports --out artifacts/demo

# Run tests
pytest -q
```

## Structure
```
ESGx-DisclosureAI/
├─ src/esgx/                  # Core package
├─ configs/                   # Pipeline configs, regex patterns, policies
├─ schemas/                   # Minimal ESG taxonomy & units
├─ data/sample/               # Toy ESG reports (text/markdown)
├─ docs/                      # Paper scaffolding & design docs
├─ tests/                     # Unit/integration tests
├─ .github/workflows/         # CI
└─ artifacts/                 # Outputs (gitignored)
```
License: MIT © 2025
