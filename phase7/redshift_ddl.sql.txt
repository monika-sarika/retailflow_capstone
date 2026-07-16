redshift_ddl.sql

CREATE SCHEMA IF NOT EXISTS retailflow;

---------------------------------------------------------
-- Customer Dimension
---------------------------------------------------------

CREATE TABLE retailflow.dim_customer
(
    customer_id     VARCHAR(50) NOT NULL,
    customer_name   VARCHAR(200),
    email           VARCHAR(200),
    city            VARCHAR(100),
    state           VARCHAR(100),
    country         VARCHAR(100)
)
DISTSTYLE KEY
DISTKEY(customer_id)
SORTKEY(customer_id);

---------------------------------------------------------
-- Product Dimension
---------------------------------------------------------

CREATE TABLE retailflow.dim_product
(
    product_id      VARCHAR(50) NOT NULL,
    product_name    VARCHAR(200),
    category        VARCHAR(100),
    unit_price      DECIMAL(10,2),
    active_flag     BOOLEAN
)
DISTSTYLE KEY
DISTKEY(product_id)
SORTKEY(category);

---------------------------------------------------------
-- Date Dimension
---------------------------------------------------------

CREATE TABLE retailflow.dim_date
(
    date_key        DATE NOT NULL,
    year            INT,
    month           INT,
    day             INT,
    quarter         INT
)
DISTSTYLE ALL
SORTKEY(date_key);

---------------------------------------------------------
-- Fact Table
---------------------------------------------------------

CREATE TABLE retailflow.fact_order_items
(
    product_id      VARCHAR(50),
    order_id        VARCHAR(50),
    quantity        INT,
    unit_price      DOUBLE PRECISION,
    line_total      DOUBLE PRECISION,
    discount_code   VARCHAR(100),
    dt              DATE
)
DISTSTYLE KEY
DISTKEY(product_id)
SORTKEY(product_id);

---------------------------------------------------------
-- Verify Tables
---------------------------------------------------------

SELECT tablename
FROM pg_tables
WHERE schemaname='retailflow';

SELECT *
FROM information_schema.tables
WHERE table_schema='retailflow';


/*=========================================================
Task 37 - Redshift Spectrum
=========================================================*/

CREATE EXTERNAL SCHEMA IF NOT EXISTS spectrum_schema
FROM DATA CATALOG
DATABASE 'retailflow_raw'
IAM_ROLE 'arn:aws:iam::209822908929:role/service-role/AWSGlueServiceRole-retailflow_raw'
CREATE EXTERNAL DATABASE IF NOT EXISTS;

CREATE EXTERNAL SCHEMA IF NOT EXISTS consumption_schema
FROM DATA CATALOG
DATABASE 'retailflow_consumption'
IAM_ROLE 'arn:aws:iam::209822908929:role/service-role/AWSGlueServiceRole-retailflow_raw';

SELECT *
FROM svv_external_tables
WHERE schemaname='consumption_schema';


/*=========================================================
Task 38 - Materialized View
=========================================================*/

CREATE MATERIALIZED VIEW retailflow.mv_daily_category_revenue
AUTO REFRESH YES
AS

SELECT
    d.date_key,
    p.category,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.quantity)            AS total_quantity,
    SUM(f.line_total)          AS revenue

FROM retailflow.fact_order_items f

JOIN retailflow.dim_product p
ON f.product_id = p.product_id

JOIN retailflow.dim_date d
ON f.dt = d.date_key

GROUP BY
d.date_key,
p.category;


/*=========================================================
Refresh MV
=========================================================*/

REFRESH MATERIALIZED VIEW retailflow.mv_daily_category_revenue;

SELECT *
FROM retailflow.mv_daily_category_revenue;


/*=========================================================
Task 40 - Dynamic Data Masking
=========================================================*/

---------------------------------------------------------
-- Users
---------------------------------------------------------

CREATE USER dataanalyst
PASSWORD 'AnalystPass123!';

CREATE USER dataengineer
PASSWORD 'EngineerPass123!';

---------------------------------------------------------
-- Roles
---------------------------------------------------------

CREATE ROLE analyst_role;

CREATE ROLE engineer_role;

---------------------------------------------------------
-- Assign Roles
---------------------------------------------------------

GRANT ROLE analyst_role
TO dataanalyst;

GRANT ROLE engineer_role
TO dataengineer;

---------------------------------------------------------
-- Schema Permission
---------------------------------------------------------

GRANT USAGE
ON SCHEMA retailflow
TO ROLE analyst_role;

GRANT USAGE
ON SCHEMA retailflow
TO ROLE engineer_role;

---------------------------------------------------------
-- Table Permission
---------------------------------------------------------

GRANT SELECT
ON TABLE retailflow.dim_customer
TO ROLE analyst_role;

GRANT SELECT
ON TABLE retailflow.dim_customer
TO ROLE engineer_role;

---------------------------------------------------------
-- Masking Policy
---------------------------------------------------------

CREATE MASKING POLICY mask_email
WITH (email VARCHAR(200))
USING ('REDACTED_PII'::VARCHAR(200));

---------------------------------------------------------
-- Attach Policy
---------------------------------------------------------

ATTACH MASKING POLICY mask_email
ON retailflow.dim_customer(email)
TO ROLE analyst_role
PRIORITY 10;

---------------------------------------------------------
-- Test
---------------------------------------------------------

SELECT customer_name,
       email
FROM retailflow.dim_customer
LIMIT 10;


/*=========================================================
Task 41 - EXPLAIN Plan
=========================================================*/

EXPLAIN

SELECT
    p.category,
    SUM(f.line_total) AS revenue

FROM retailflow.fact_order_items f

JOIN retailflow.dim_product p
ON f.product_id = p.product_id

GROUP BY p.category;