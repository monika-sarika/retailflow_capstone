# RetailFlow Capstone Project – AWS Data Engineer Track
## Project Overview
RetailFlow is a fictional mid-size e-commerce company.
As the Data Engineer, your mission is to build their first cloud data platform.
You will take raw, messy order data through a governed data lake, into two parallel analytics engines (Amazon Redshift and Databricks), and finally deliver business-ready dashboards.

This project simulates real-world challenges such as:

Schema evolution

Data quality enforcement

Governance & access control

Cost optimization

Multi-engine analytics

## Learning Objectives

By completing this capstone, you will:

Write Python/Boto3 scripts for S3 ingestion with logging and retry logic.

Design a three-zone S3 data lake (Bronze/Silver/Gold).

Implement governance with AWS Lake Formation LF-Tags.

Build Glue ETL jobs with idempotency and data quality rules.

Model and load a Redshift star schema and query S3 via Spectrum.

Build a Databricks Delta Lake medallion pipeline with Auto Loader, Delta Live Tables, and Unity Catalog.

Present results through dashboards in both Redshift and Databricks.

## Environments
AWS Free Tier → S3, IAM, Glue, Lake Formation, Athena, Redshift Serverless, CloudWatch

VS Code → Python project, Boto3 scripts, Glue ETL authoring, git repo, AWS CLI

Google Colab → Synthetic data generation, profiling, charts

Databricks Free Trial → Delta Lake, Auto Loader, Delta Live Tables, Unity Catalog, Workflows, SQL Warehouse

## Cost & Safety Guardrails

Create a $5 AWS Budget Alert immediately.

Use Redshift Serverless (8 RPU, auto-pause).

Use Glue G.1X workers (2–3 max).

Keep datasets small (tens of thousands of rows).

Tear down resources after each phase.

## Dataset
Synthetic dataset generated with Python’s Faker library:

customers.csv → 5,000 rows (null/malformed emails, duplicate IDs)

products.csv → 800 rows (category, unit_price, active_flag)

orders_day1.json → 20,000 rows (order headers)

order_items_day1.json → 55,000 rows (order lines)

orders_day2.json / order_items_day2.json → Schema evolution (new discount_code column)

clickstream_day1/day2.json → 15,000/day (web session events for streaming demo)

Deliberate data quality issues include nulls, duplicates, invalid references, negative quantities, and schema drift.

## Project Phases
### Phase 0 
 Environment Setup → AWS account, budget, IAM, CLI, Colab, Databricks trial

### Phase 1 
 Synthetic Data Generation & Profiling → Generate data, profile with Pandas, create charts

### Phase 2 
 Boto3 Ingestion Utility → Python package for S3 ingestion with logging + retry

### Phase 3  
 S3 Data Lake Foundations → Raw/Curated/Consumption zones, partitioning, encryption, lifecycle rules

### Phase 4 
 Glue Catalog & Athena → Crawlers, schema fixes, partition projection, cost comparison queries

### Phase 5 
 Lake Formation Governance → LF-Tags, IAM roles, access proof

### Phase 6 
 Glue ETL (Raw → Silver) → PySpark ETL, bookmarks, schema evolution, data quality rules, quarantine

### Phase 7 
 Redshift Analytics → Star schema, COPY load, Spectrum, materialized views, WLM, masking, EXPLAIN plan

### Phase 8 
 Databricks Lakehouse → Bronze/Silver/Gold Delta tables, Auto Loader, Delta Live Tables, Unity Catalog, workflows, dashboards

### Phase 9 
 Final Integration Report → Architecture diagram, cost review, reflection

## Deliverables Checklist
Git repo with README + ARCHITECTURE.md

Data generation notebook + profile report + charts

Boto3 ingestion package + logs

S3 bucket screenshots (structure, versioning, encryption, lifecycle)

Athena cost comparison report

Lake Formation governance report + screenshots

Glue ETL job + DQDL ruleset + bookmarks proof + CloudWatch screenshot

Redshift SQL scripts + performance report

Databricks notebooks + pipeline JSON + workflow JSON + dashboard screenshot

Final report (diagram, cost review, reflection)

## Evaluation Rubric
Python & Ingestion Quality (15%) → Boto3 utility design, retry/logging, code cleanliness

Data Lake Design (20%) → Zone structure, partitioning, security, lifecycle policy correctness

Governance (10%) → LF-Tags and Unity Catalog access control correctness

Glue ETL & Data Quality (25%) → Bookmark correctness, schema evolution handling, DQDL rule coverage, quarantine routing

Redshift Track (17%) → Schema design, load correctness, Spectrum, WLM/QMR, masking, performance tuning evidence

Databricks Track (13%) → Auto Loader, DLT expectations, Unity Catalog, Workflow orchestration, dashboard

This README serves as the master guide for the entire capstone project. Each phase should have its own README or documentation file inside the repo for detailed steps, commands, and code.
