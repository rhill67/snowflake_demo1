# Demo Talking Points

## Snowflake
- X-Small warehouse + auto-suspend/auto-resume demonstrates cost awareness.
- Bronze preserves source-aligned structures.
- Silver standardizes and validates.
- Gold exposes business-facing data products.
- Data quality checks cover uniqueness, referential integrity, valid financial ranges, and derived totals.
- MERGE demonstrates incremental CDC-style processing and idempotency.
- Zero-copy cloning supports dev/QA isolation.
- Time Travel supports historical investigation and recovery.

## dbt
- `source()` references raw Snowflake objects.
- `ref()` creates model dependencies and the DAG.
- Staging models standardize source data.
- Marts expose reusable business models.
- Tests enforce data contracts.
- Macros reduce repeated SQL.
- Incremental materialization controls how much data is processed.
- CI/CD can validate dbt changes before merge.

## Lead-level framing
Do not present this as "I made some SQL scripts."

Present it as:
"I built a small production-minded pattern showing ingestion, layered transformations, data quality, incremental processing, governed development environments, and software-engineering practices around analytics SQL."
