 Redshift_governance.sql

-- Create Users
------------------------------------------------------

CREATE USER dataanalyst
PASSWORD 'AnalystPass123!';

CREATE USER dataengineer
PASSWORD 'EngineerPass123!';

------------------------------------------------------
-- Create Roles
------------------------------------------------------

CREATE ROLE analyst_role;
CREATE ROLE engineer_role;

------------------------------------------------------
-- Grant Roles
------------------------------------------------------

GRANT ROLE analyst_role
TO dataanalyst;

GRANT ROLE engineer_role
TO dataengineer;

------------------------------------------------------
-- Schema Permissions
------------------------------------------------------

GRANT USAGE
ON SCHEMA retailflow
TO ROLE analyst_role;

GRANT USAGE
ON SCHEMA retailflow
TO ROLE engineer_role;

------------------------------------------------------
-- Table Permissions
------------------------------------------------------

GRANT SELECT
ON TABLE retailflow.dim_customer
TO ROLE analyst_role;

GRANT SELECT
ON TABLE retailflow.dim_customer
TO ROLE engineer_role;

------------------------------------------------------
-- Create Email Masking Policy
------------------------------------------------------

CREATE MASKING POLICY mask_email
WITH (email VARCHAR(200))
USING ('REDACTED_PII'::VARCHAR(200));

------------------------------------------------------
-- Attach Policy
------------------------------------------------------

ATTACH MASKING POLICY mask_email
ON retailflow.dim_customer (email)
TO ROLE analyst_role
PRIORITY 10;

------------------------------------------------------
-- Test as Analyst
------------------------------------------------------
-- Disconnect and reconnect as:
-- User : dataanalyst
-- Password : AnalystPass123!

SELECT customer_name,
       email
FROM retailflow.dim_customer
LIMIT 10;

------------------------------------------------------
-- Test as Engineer
------------------------------------------------------
-- Disconnect and reconnect as:
-- User : dataengineer
-- Password : EngineerPass123!

SELECT customer_name,
       email
FROM retailflow.dim_customer
LIMIT 10;