USE WAREHOUSE LENNAR_DEMO_WH;

-- 1. Inspect the current row.
SELECT *
FROM LENNAR_DEMO.SILVER.ORDERS
WHERE ORDER_ID = 1000;

-- 2. Capture and save this timestamp BEFORE the update.
SELECT CURRENT_TIMESTAMP();

-- 3. Make a deliberate change.
UPDATE LENNAR_DEMO.SILVER.ORDERS
SET STATUS = 'TIME_TRAVEL_TEST'
WHERE ORDER_ID = 1000;

-- 4. Verify the current value.
SELECT *
FROM LENNAR_DEMO.SILVER.ORDERS
WHERE ORDER_ID = 1000;

-- 5. Replace the timestamp below with the value captured above.
SELECT *
FROM LENNAR_DEMO.SILVER.ORDERS
AT (
    TIMESTAMP => '2026-08-26 00:00:00.000 -0500'::TIMESTAMP_TZ
)
WHERE ORDER_ID = 1000;

-- Alternative if you know the update occurred within the last minute:
SELECT *
FROM LENNAR_DEMO.SILVER.ORDERS
AT (OFFSET => -60)
WHERE ORDER_ID = 1000;
