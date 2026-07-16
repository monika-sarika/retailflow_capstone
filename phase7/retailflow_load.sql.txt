retailflow_load.sql


---------------------------------------------------------
-- Load Customer Dimension
---------------------------------------------------------

COPY retailflow.dim_customer
FROM 's3://retailflow-bucket/manifests/customers_manifest.json'
IAM_ROLE 'arn:aws:iam::209822908929:role/service-role/AWSGlueServiceRole-retailflow_raw'
FORMAT AS PARQUET;

SELECT COUNT(*) AS dim_customer_count
FROM retailflow.dim_customer;

---------------------------------------------------------
-- Load Product Dimension
---------------------------------------------------------

COPY retailflow.dim_product
FROM 's3://retailflow-bucket/manifests/products_manifest.json'
IAM_ROLE 'arn:aws:iam::209822908929:role/service-role/AWSGlueServiceRole-retailflow_raw'
FORMAT AS PARQUET;

SELECT COUNT(*) AS dim_product_count
FROM retailflow.dim_product;

---------------------------------------------------------
-- Load Fact Table from Spectrum
---------------------------------------------------------

INSERT INTO retailflow.fact_order_items
(
    order_id,
    product_id,
    quantity,
    unit_price,
    line_total,
    discount_code,
    dt
)
SELECT
    order_id,
    product_id,
    quantity,
    unit_price,
    line_total,
    discount_code,
    dt
FROM spectrum_schema.fact_order_items;

SELECT COUNT(*) AS fact_order_items_count
FROM retailflow.fact_order_items;

---------------------------------------------------------
-- Populate Date Dimension
---------------------------------------------------------

INSERT INTO retailflow.dim_date
(
    date_key,
    year,
    month,
    day,
    quarter
)
SELECT DISTINCT
    dt AS date_key,
    EXTRACT(YEAR FROM dt) AS year,
    EXTRACT(MONTH FROM dt) AS month,
    EXTRACT(DAY FROM dt) AS day,
    EXTRACT(QUARTER FROM dt) AS quarter
FROM retailflow.fact_order_items
WHERE dt IS NOT NULL;

SELECT *
FROM retailflow.dim_date
ORDER BY date_key;

---------------------------------------------------------
-- Verify Counts
---------------------------------------------------------

SELECT COUNT(*) FROM retailflow.dim_customer;
SELECT COUNT(*) FROM retailflow.dim_product;
SELECT COUNT(*) FROM retailflow.fact_order_items;
SELECT COUNT(*) FROM retailflow.dim_date;