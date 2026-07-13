RetailFlow Data Lake Architecture

Overview

The **RetailFlow Data Lake** is implemented on **Amazon S3**, providing scalable, secure, and cost‑optimized storage for retail datasets.  
It follows a **multi‑zone architecture** to support ingestion, curation, and consumption workflows.

--------------------------------------------------------------------

Data Lake Zones

| Zone | Prefix | Purpose |
|------|---------|----------|
| **Raw (Bronze)** | `raw/` | Stores unprocessed data directly from source systems. Partitioned by dataset and date (`dt=YYYY‑MM‑DD`). |
| **Curated (Silver)** | `curated/` | Contains cleaned and standardized data ready for transformation. |
| **Consumption (Gold)** | `consumption/` | Holds aggregated, analytics‑ready datasets for BI tools and dashboards. |

---------------------------------------------------------------------------------------------

Folder Structure Example
retailflow-bucket/
├── raw/
│   ├── clickstream/
│   │   ├── dt=2026-07-08/
│   │   └── dt=2026-07-09/
│   ├── order_items/
│   │   ├── dt=2026-07-08/
│   │   └── dt=2026-07-09/
│   └── orders/
│       ├── dt=2026-07-08/
│       └── dt=2026-07-09/
├── curated/
└── consumption/


-------------------------------------------------------------------------------

Security & Versioning
- **Bucket Versioning:** Enabled — preserves all object versions for recovery.  
- **MFA Delete:** Disabled (optional for production).  
- **Default Encryption:** Server‑side encryption with Amazon S3‑managed keys (**SSE‑S3**) and **Bucket Key Enabled** to reduce KMS costs.  
- **Blocked Encryption Types:** SSE‑C (customer‑provided keys).

-----------------------------------------------------------------

Lifecycle Policy
**Rule Name:** `transition_raw_lifecycle`  
- **Scope:** Prefix `raw/`  
- **Transition:** Move objects to **Standard‑IA** after 30 days.  
- **Cleanup:** Delete incomplete multipart uploads after 7 days.  
- **Status:** Enabled  

This policy optimizes storage costs while maintaining accessibility for recent data.

-----------------------------------------------------------

AWS Region
- **Region:** Asia Pacific (Mumbai) — `ap-south-1`  
- **Bucket ARN:** `arn:aws:s3:::retailflow-bucket`

------------------------------------------------------------

