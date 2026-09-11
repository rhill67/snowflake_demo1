# Snowflake Lennar Python Demo

This project turns the earlier SQL-only Snowflake demo into a Python-controlled deployment utility.

The wrapper uses the official Snowflake Python Connector and external SQL files. It supports:

```text
build   Create warehouse, database, Bronze/Silver/Gold schemas, stage, file format, and Bronze tables.
deploy  Run build, PUT the CSV files, COPY Bronze data, create Silver/Gold, run DQ SQL, and run a CDC-style MERGE.
status  Print connection context, row counts, object inventory, order status counts, and monthly revenue.
delete  Drop the demo database and warehouse. Requires --yes.
```

Default database:

```text
SF_LENNAR_PYTHON_DEMO
```

Default warehouse:

```text
SF_LENNAR_PYTHON_DEMO_WH
```

## Architecture

```text
Python CLI
   |
   +--> Snowflake Python Connector
   |
   +--> 01_infrastructure.sql
   +--> 02_bronze.sql
   +--> PUT local CSV files
   +--> 03_copy_bronze.sql
   +--> 04_silver.sql
   +--> 05_data_quality.sql
   +--> 06_gold.sql
   +--> 07_cdc_merge.sql

BRONZE -> SILVER -> GOLD
```

## Setup

```bash
unzip sf_lennar_python_demo.zip
cd sf_lennar_python_demo

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy the environment template:

```bash
cp .env.example .env
nano .env
```

Example:

```dotenv
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ROLE=ACCOUNTADMIN
SNOWFLAKE_WAREHOUSE=SF_LENNAR_PYTHON_DEMO_WH
SNOWFLAKE_DATABASE=SF_LENNAR_PYTHON_DEMO
```

For browser authentication instead of a password:

```dotenv
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_USER=your_user
SNOWFLAKE_AUTHENTICATOR=externalbrowser
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

`.env` is excluded by `.gitignore`.

## CSV inputs

The `data/` folder contains small sample files so the demo runs immediately:

```text
customers.csv
products.csv
orders.csv
sales.csv
```

You can replace these with the larger CSVs from the original demo.

Expected columns:

```text
customers.csv
customer_id,first_name,last_name,email,signup_date,country

products.csv
product_id,product_name,category,price,active

orders.csv
order_id,customer_id,order_date,status

sales.csv
sale_id,order_id,product_id,quantity,unit_price,discount,total_amount
```

## Build

```bash
python sf_lennar_demo.py build -v
```

This creates the Snowflake infrastructure and Bronze tables, but does not load data.

## Deploy

```bash
python sf_lennar_demo.py deploy -v
```

The deploy sequence is:

```text
1. Create X-Small auto-suspending warehouse
2. Create SF_LENNAR_PYTHON_DEMO
3. Create BRONZE / SILVER / GOLD
4. Create CSV file format and internal stage
5. Create Bronze tables
6. PUT customers/products/orders/sales CSVs
7. COPY the CSVs into Bronze
8. Build cleaned Silver tables
9. Execute data-quality checks
10. Create Gold revenue views
11. Run CDC-style MERGE
12. Print deployment status
```

To use another input directory:

```bash
python sf_lennar_demo.py deploy --data-dir /path/to/csvs -v
```

## Status

```bash
python sf_lennar_demo.py status -v
```

This prints and logs:

- Snowflake account/user/role/warehouse
- Bronze and Silver row counts
- object inventory
- order counts by status
- Gold monthly revenue

## Delete

A delete without confirmation is rejected:

```bash
python sf_lennar_demo.py delete
```

Actual cleanup:

```bash
python sf_lennar_demo.py delete --yes -v
```

This drops both:

```text
SF_LENNAR_PYTHON_DEMO
SF_LENNAR_PYTHON_DEMO_WH
```

## Logging

The script writes to standard output and to:

```text
logs/sf_lennar_python_demo.log
```

Verbose mode shows SQL activity:

```bash
python sf_lennar_demo.py deploy -v
```

Watch the log:

```bash
tail -f logs/sf_lennar_python_demo.log
```

## Useful command sequence for the interview

```bash
python sf_lennar_demo.py deploy -v
python sf_lennar_demo.py status
```

Then show the Snowflake objects and explain:

> I first built the environment manually in SQL. I then automated the same lifecycle with Python using the Snowflake Connector. Python handles orchestration, parameters, logging, deployment and teardown, while Snowflake DDL/DML stays in external SQL files so it remains easy to review and maintain. The deployment follows Bronze, Silver and Gold layers, includes data-quality checks, and demonstrates a CDC-style MERGE.

For production, mention that you would normally use least-privilege service roles, a secrets manager, CI/CD, structured observability, and potentially Terraform for infrastructure and dbt for transformation management.

## Project layout

```text
sf_lennar_python_demo/
|-- sf_lennar_demo.py
|-- README.md
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- data/
|   |-- customers.csv
|   |-- products.csv
|   |-- orders.csv
|   `-- sales.csv
|-- logs/
`-- sql/
    |-- 01_infrastructure.sql
    |-- 02_bronze.sql
    |-- 03_copy_bronze.sql
    |-- 04_silver.sql
    |-- 05_data_quality.sql
    |-- 06_gold.sql
    |-- 07_cdc_merge.sql
    |-- 08_status.sql
    `-- 09_delete.sql
```
