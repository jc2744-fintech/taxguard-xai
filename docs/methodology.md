# Methodology

1. **Ingestion**: Load text/markdown (PDF/HTML readers can be added) and normalize whitespace/sections.
2. **Extraction**: Regex-driven patterns (configurable) to pull candidate values + units.
3. **Normalization**: Convert to canonical units (e.g., kg→t, kWh→MWh) and map to taxonomy.
4. **Validation**: Completeness checks, unit checks, non-negativity, and simple YoY drift vs. previous year.
5. **Report Generation**: Markdown + JSON summary with flags, provenance, and disclaimers.
6. **Audit Trail**: Artifacts include extraction hits with spans and pattern IDs.
