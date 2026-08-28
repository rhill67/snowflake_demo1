# Lennar Data Engineering Demo

A compact interview demo showing a production-minded data engineering workflow with **Snowflake + dbt**.

The project uses four simple source datasets:

- `customers.csv`
- `products.csv`
- `orders.csv`
- `sales.csv`

It demonstrates:

1. Snowflake database/schema/warehouse setup
2. Internal stages and `COPY INTO`
3. Bronze / Silver / Gold layering
4. Data quality and referential-integrity checks
5. Incremental / CDC-style `MERGE`
6. Zero-copy cloning
7. Time Travel
8. dbt `source()`, `ref()`, models, tests, macros, and incremental materialization
9. A simple GitHub Actions dbt CI example

> This is intentionally small enough to explain in an interview. It is not meant to be a full production platform.

---

## Architecture

```text
CSV source files
      |
      v
Snowflake internal stage
      |
      v
BRONZE
raw/source-aligned tables
      |
      v
SILVER
cleaned + standardized + validated
      |
      v
GOLD
business-facing data products
      |
      +--> Analytics
      +--> BI
      +--> AI / downstream consumers
```

The dbt portion models the same basic flow:

```text
Snowflake BRONZE
      |
      v
dbt staging models
      |
      v
dbt marts
      |
      v
tests / docs / lineage
```

---

## Repository Layout

```text
lennar-data-engineering-demo/
|
|-- data/
|   |-- customers.csv
|   |-- products.csv
|   |-- orders.csv
|   `-- sales.csv
|
|-- snowflake/
|   `-- sql/
|       |-- 01_setup.sql
|       |-- 02_bronze_tables.sql
|       |-- 03_stage.sql
|       |-- 04_copy_into.sql
|       |-- 05_silver.sql
|       |-- 06_quality_checks.sql
|       |-- 07_gold.sql
|       |-- 08_incremental_merge.sql
|       |-- 09_zero_copy_clone.sql
|       `-- 10_time_travel.sql
|
|-- dbt/
|   |-- dbt_project.yml
|   |-- profiles.yml.example
|   |-- models/
|   |   |-- staging/
|   |   `-- marts/
|   |-- macros/
|   `-- tests/
|
|-- .github/workflows/dbt-ci.yml
|-- requirements.txt
`-- README.md
```

---

# Part 1 - Snowflake Demo

## 1. Create a Snowflake Trial

Use a Snowflake trial account and select AWS if you want the environment to align with the target role.

Open a SQL worksheet and run the files in `snowflake/sql/` in numeric order.

## 2. Run Setup

Run:

```text
snowflake/sql/01_setup.sql
```

This creates:

- `LENNAR_DEMO`
- `BRONZE`
- `SILVER`
- `GOLD`
- `LENNAR_DEMO_WH`

The warehouse is intentionally `X-SMALL` with auto-suspend and auto-resume to demonstrate cost awareness.

## 3. Create Bronze Tables

Run:

```text
snowflake/sql/02_bronze_tables.sql
```

The tables match the four CSV schemas in this repository.

## 4. Create Stage and Upload CSV Files

Run:

```text
snowflake/sql/03_stage.sql
```

Then upload the four files in `data/` to:

```text
@LENNAR_DEMO.BRONZE.CSV_STAGE
```

Verify with:

```sql
LIST @LENNAR_DEMO.BRONZE.CSV_STAGE;
```

## 5. Load Bronze

Run:

```text
snowflake/sql/04_copy_into.sql
```

This uses Snowflake `COPY INTO`.

## 6. Build Silver

Run:

```text
snowflake/sql/05_silver.sql
```

Silver performs:

- trimming
- casing normalization
- basic validation
- derived sales amount calculation

## 7. Run Data Quality Checks

Run:

```text
snowflake/sql/06_quality_checks.sql
```

Checks include:

- duplicate customers
- duplicate orders
- orders without customers
- sales without orders
- sales without products
- invalid quantities/prices/discounts
- source total vs calculated total

## 8. Build Gold

Run:

```text
snowflake/sql/07_gold.sql
```

Gold exposes:

- order revenue
- product revenue
- customer revenue
- monthly revenue

## 9. Incremental / CDC-Style MERGE

Run:

```text
snowflake/sql/08_incremental_merge.sql
```

This demonstrates:

- one update
- one insert
- deterministic matching on `ORDER_ID`
- rerunnable/idempotent behavior

This is a **CDC-style downstream merge**, not source-log CDC.

## 10. Zero-Copy Clone

Run:

```text
snowflake/sql/09_zero_copy_clone.sql
```

This clones the full demo database into:

```text
LENNAR_DEMO_DEV
```

It then changes an order only in the clone to demonstrate isolation.

## 11. Time Travel

Run:

```text
snowflake/sql/10_time_travel.sql
```

Follow the comments in the file. Capture a timestamp before the update, then use it to query the earlier version.

---

# Part 2 - dbt Demo

## Prerequisites

Python 3.10+ is sufficient for this small demo.

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install:

```bash
pip install -r requirements.txt
```

## Configure dbt

Copy:

```text
dbt/profiles.yml.example
```

to your local dbt profiles directory as `profiles.yml`.

Typical locations:

```text
Linux/macOS: ~/.dbt/profiles.yml
Windows:     %USERPROFILE%\.dbt\profiles.yml
```

Set these environment variables rather than hard-coding credentials:

```text
SNOWFLAKE_ACCOUNT
SNOWFLAKE_USER
SNOWFLAKE_PASSWORD
SNOWFLAKE_ROLE
SNOWFLAKE_WAREHOUSE
```

Then:

```bash
cd dbt
dbt debug
```

## Run the dbt Project

```bash
dbt run
dbt test
```

Or:

```bash
dbt build
```

Build one model:

```bash
dbt run --select stg_customers
```

Build a model and its downstream dependencies:

```bash
dbt build --select stg_orders+
```

---

# dbt Concepts Demonstrated

## `source()`

Raw Snowflake tables are declared in:

```text
models/staging/sources.yml
```

Example:

```sql
select *
from {{ source('bronze', 'orders') }}
```

## `ref()`

dbt-managed dependencies use `ref()`:

```sql
select *
from {{ ref('stg_orders') }}
```

This allows dbt to build the DAG automatically.

## Incremental Model

`stg_orders.sql` is configured as an incremental model using `ORDER_ID` as the unique key.

The model demonstrates:

```jinja
{% if is_incremental() %}
...
{% endif %}
```

## Tests

The project includes:

- `unique`
- `not_null`
- `accepted_values`
- `relationships`
- custom SQL data test

## Macro

`macros/clean_text.sql` provides a small reusable text-cleaning macro.

---

# CI/CD Example

`.github/workflows/dbt-ci.yml` contains a small GitHub Actions example.

It:

1. checks out the repository
2. installs Python
3. installs dbt
4. runs `dbt deps`
5. runs `dbt parse`
6. optionally runs `dbt build` when Snowflake secrets are configured

For a real enterprise implementation, branch protection and required pull-request checks would be enabled in GitHub.

---

# Five-Minute Interview Walkthrough

A concise demo explanation:

> I built a small Snowflake data platform using four source files. The files land through an internal stage and `COPY INTO` into a source-aligned Bronze layer. Silver standardizes and validates the data, and Gold exposes business-oriented order, customer, product, and monthly revenue models.
>
> I added referential-integrity and financial data-quality checks, then implemented a Snowflake `MERGE` to demonstrate incremental CDC-style processing. I also used zero-copy cloning to create an isolated development environment and Time Travel to query a historical version of an order.
>
> I then modeled the same transformation pattern with dbt using `source()`, `ref()`, staging models, marts, tests, a macro, and an incremental model. Finally, I included a lightweight CI workflow to show how the project could be validated through pull requests before production deployment.

---

# Lead Data Engineer Talking Points

Use these ideas while explaining the project:

- Bronze preserves source alignment and replayability.
- Silver is where standardization and trust are established.
- Gold exposes business-facing data products rather than raw source structures.
- `MERGE` supports deterministic incremental processing.
- Data quality includes both technical validity and referential integrity.
- dbt provides modularity, lineage, testing, documentation, and dependency management.
- Snowflake compute should be intentionally sized and automatically suspended when idle.
- Zero-copy cloning is useful for development, QA, and regression testing.
- Time Travel supports recovery, auditing, and troubleshooting.
- AI-generated code should still pass normal code review, tests, and CI/CD controls.

---

## Important Note

The sample CSV files in this repository are synthetic demo data matching the schemas used by the SQL and dbt code. If you already have your original CSV files, you can replace the files under `data/` as long as their column order and datatypes match the table definitions.
