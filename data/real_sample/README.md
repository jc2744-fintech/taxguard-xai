# Real public smoke snapshot

This directory contains **15 organization-year rows for three Washington nonprofit organizations**. The values are public Form 990 summary facts presented by ProPublica Nonprofit Explorer from IRS-derived data. It is intentionally small enough to inspect manually and run in CI.

## Included

- Organization-level identifiers, tax years, top-line financial values, mission/narrative summaries, and source URLs.
- A provenance table and SHA-256 manifest.
- Derived temporal and analytical peer edges.

## Excluded

Person names, individual compensation rows, street addresses, phone numbers, email addresses, and any ground-truth compliance labels.

## Critical boundary

The snapshot supports smoke tests, longitudinal feature checks, weak-supervision demonstrations, and anomaly-discovery examples. It is not statistically representative and cannot establish model performance or misconduct. Verify every value against the original filing before consequential use.

## Refresh

Use either:

```bash
form990-xai fetch-propublica --ein 91-0564748 --ein 91-1935159 --ein 91-0565006 --output-dir data/refresh
```

or the full official IRS path:

```bash
form990-xai discover --year 2026
form990-xai download --year 2026 --period 06A --output-dir data/raw/irs
form990-xai ingest --archive data/raw/irs/2026_TEOS_XML_06A.zip --output-dir data/processed/2026_06A --allow-demo-salt
```

Use a private study-specific `FORM990_ENTITY_SALT` instead of `--allow-demo-salt` whenever person/entity linkage will be retained.
