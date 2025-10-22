# Architecture

- `esgx.ingest`: readers & text normalization
- `esgx.extract`: pattern-based matchers
- `esgx.normalize`: unit conversions and canonicalization
- `esgx.mapping`: map candidates to taxonomy elements
- `esgx.validate`: policy checks and drift detection
- `esgx.generate`: report assembly (Markdown/JSON)
- `esgx.audit`: provenance & logs
- `esgx.cli`: Typer CLI
