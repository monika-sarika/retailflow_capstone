# Phase 6 – Job Bookmarks Proof (Raw → Silver ETL)

## Objective

Demonstrate that AWS Glue Job Bookmarks make the ETL job idempotent by ensuring only newly arrived files are processed during subsequent executions.

---

# Environment

- AWS Glue Version: 4.0
- Job Name: `capstone_raw_to_silver_etl`
- Source Database: `retailflow_raw`
- Target Database: `curated_retailflow`
- Output Format: Parquet
- Job Bookmarks: **Enabled**

---

# Job Bookmark Execution Verification

## Objective

Verify that AWS Glue Job Bookmarks process only newly added files during incremental ETL execution.

---

## Run 1 – Initial Load (Day 1)

The Job Bookmark was reset before executing the first run.

```bash
aws glue reset-job-bookmark --job-name capstone_raw_to_silver_etl
```

The Glue job processed all available raw files.

### CloudWatch Log Evidence

```
Orders count: 20000
[Bookmark] Orders records processed this run: 20000

[Bookmark] OrderItems records processed this run: 49995
```

**Screenshot**

![alt text](<bookmark day1.png>)

### Observation

- Bookmark state initialized.
- All Day 1 files were processed.
- Bookmark metadata was updated after successful job completion.

---

## Run 2 – Incremental Load (Day 2)

Only the Day 2 raw files were uploaded to the S3 Raw bucket.

The Glue job was executed again with Job Bookmarks enabled.

### CloudWatch Log Evidence

```
Orders count: 4000
[Bookmark] Orders records processed this run: 4000

[Bookmark] OrderItems records processed this run: 9901
```

**Screenshot**

![`bookmark_day2.png`](<bookmark day2.png>)

### Observation

Compared to the first execution:

| Dataset | Run 1 | Run 2 |
|----------|-------|-------|
| Orders | 20,000 | 4,000 |
| Order Items | 49,995 | 9,901 |

The second execution processed only the newly added Day 2 files.

Previously processed Day 1 files were skipped automatically by AWS Glue Job Bookmarks.