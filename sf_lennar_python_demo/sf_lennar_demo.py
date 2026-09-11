#!/usr/bin/env python3
import argparse, logging, os, sys
from pathlib import Path
import snowflake.connector, sqlparse
from dotenv import load_dotenv

BASE=Path(__file__).resolve().parent
SQL=BASE/"sql"
DATA=BASE/"data"
LOGS=BASE/"logs"
DB="SF_LENNAR_PYTHON_DEMO"
WH="SF_LENNAR_PYTHON_DEMO_WH"

def logger(verbose, logfile):
    logfile.parent.mkdir(parents=True, exist_ok=True)
    log=logging.getLogger("sf_demo"); log.handlers.clear()
    log.setLevel(logging.DEBUG if verbose else logging.INFO)
    fmt=logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")
    sh=logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); log.addHandler(sh)
    fh=logging.FileHandler(logfile); fh.setLevel(logging.DEBUG); fh.setFormatter(fmt); log.addHandler(fh)
    return log

def render(text, vals):
    for k,v in vals.items(): text=text.replace("{{"+k+"}}", v)
    return text

def run_file(cur, name, vals, log, show=False):
    p=SQL/name; log.info("SQL file: %s", p.name)
    for stmt in [s.strip() for s in sqlparse.split(render(p.read_text(), vals)) if s.strip()]:
        log.debug("SQL> %s", " ".join(stmt.split())[:1200]); cur.execute(stmt)
        if show and cur.description:
            headers=[d[0] for d in cur.description]; rows=cur.fetchall()
            log.info(" | ".join(headers))
            for r in rows: log.info(" | ".join(str(x) for x in r))

def put_csvs(cur, data_dir, db, log):
    for name in ["customers.csv","products.csv","orders.csv","sales.csv"]:
        p=(data_dir/name).resolve()
        if not p.exists(): raise FileNotFoundError(f"Missing {p}")
        log.info("Uploading %s", name)
        cur.execute(f"PUT 'file://{p.as_posix()}' @{db}.BRONZE.CSV_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE")

def build(cur, vals, log):
    log.info("=== BUILD START ===")
    run_file(cur,"01_infrastructure.sql",vals,log)
    run_file(cur,"02_bronze.sql",vals,log)
    log.info("=== BUILD COMPLETE ===")

def deploy(cur, vals, data_dir, log):
    log.info("=== DEPLOY START ==="); build(cur,vals,log)
    put_csvs(cur,data_dir,vals["DATABASE"],log)
    for f in ["03_copy_bronze.sql","04_silver.sql","05_data_quality.sql","06_gold.sql","07_cdc_merge.sql"]:
        run_file(cur,f,vals,log)
    status(cur,vals,log)
    log.info("=== DEPLOY COMPLETE ===")

def status(cur, vals, log):
    log.info("=== STATUS ==="); run_file(cur,"08_status.sql",vals,log,show=True)

def main():
    load_dotenv(BASE/".env")
    p=argparse.ArgumentParser(description="Snowflake Lennar Python demo")
    p.add_argument("command",choices=["build","deploy","status","delete"])
    p.add_argument("--account",default=os.getenv("SNOWFLAKE_ACCOUNT"))
    p.add_argument("--user",default=os.getenv("SNOWFLAKE_USER"))
    p.add_argument("--password",default=os.getenv("SNOWFLAKE_PASSWORD"))
    p.add_argument("--authenticator",default=os.getenv("SNOWFLAKE_AUTHENTICATOR"))
    p.add_argument("--role",default=os.getenv("SNOWFLAKE_ROLE","ACCOUNTADMIN"))
    p.add_argument("--database",default=os.getenv("SNOWFLAKE_DATABASE",DB))
    p.add_argument("--warehouse",default=os.getenv("SNOWFLAKE_WAREHOUSE",WH))
    p.add_argument("--data-dir",type=Path,default=Path(os.getenv("SNOWFLAKE_DEMO_DATA_DIR",DATA)))
    p.add_argument("--log-file",type=Path,default=LOGS/"sf_lennar_python_demo.log")
    p.add_argument("-v","--verbose",action="store_true")
    p.add_argument("--yes",action="store_true")
    a=p.parse_args()
    if not a.account or not a.user: p.error("SNOWFLAKE_ACCOUNT and SNOWFLAKE_USER are required")
    a.database=a.database.upper(); a.warehouse=a.warehouse.upper()
    log=logger(a.verbose,a.log_file)
    vals={"DATABASE":a.database,"WAREHOUSE":a.warehouse}
    kwargs=dict(account=a.account,user=a.user,role=a.role,warehouse=a.warehouse)
    if a.password: kwargs["password"]=a.password
    elif a.authenticator: kwargs["authenticator"]=a.authenticator
    else: raise SystemExit("Set SNOWFLAKE_PASSWORD or SNOWFLAKE_AUTHENTICATOR.")
    log.info("Command=%s database=%s warehouse=%s",a.command,a.database,a.warehouse)
    conn=None
    try:
        conn=snowflake.connector.connect(**kwargs)
        log.info("Connected successfully")
        with conn.cursor() as cur:
            if a.command=="build": build(cur,vals,log)
            elif a.command=="deploy": deploy(cur,vals,a.data_dir,log)
            elif a.command=="status": status(cur,vals,log)
            else:
                if not a.yes: raise SystemExit("Refusing delete. Re-run with delete --yes")
                run_file(cur,"09_delete.sql",vals,log)
    except Exception:
        log.exception("Command failed"); return 1
    finally:
        if conn: conn.close()
    return 0

if __name__=="__main__": raise SystemExit(main())
