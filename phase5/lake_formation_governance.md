# 🧩 Lake Formation Governance — Phase 5

## 🎯 Objective
Demonstrate fine‑grained, column‑level access control in AWS Lake Formation using LF‑Tags and role‑based permissions.

---

## 🧱 Architecture Overview
| Layer | Description |
|-------|--------------|
| **Data Lake Admins** | `AWSGlueServiceRole-retailflow_raw`, `data_engineer` — full governance privileges |
| **Data Analyst** | Restricted user with LF‑Tag‑based access to non‑PII data |
| **Database** | `retailflow_raw` — Lake Formation‑managed permissions enabled |
| **Table** | `customers` — tagged columns for PII governance |

---

## 🏷️ LF‑Tag Definitions
| LF‑Tag Key | LF‑Tag Value | Assigned To |
|-------------|--------------|-------------|
| `data_sensitivity` | `Confidential` | Table `customers` |
| `data_sensitivity` | `PII` | Columns `email` |

---

## 🔐 Permissions Summary
| Principal | LF‑Tag Access | Scope | Result |
|------------|---------------|--------|---------|
| `data_engineer` | `Confidential`, `PII` | Full table | Sees all columns |
| `data_analyst` | `Confidential` only | Tag‑based | Sees non‑PII columns only |
| `IAMAllowedPrincipals` | ❌ Revoked | Global | Prevents IAM bypass |

---

## ⚙️ Configuration Highlights
- **Lake Formation → Data Catalog settings:** IAM‑based access disabled.  
- **Table owner:** Changed to `data_engineer`.  
- **LF‑Tags applied:** Saved as new version after schema update.  
- **Crawler classifier:** CSV with header enabled (`Has headings = true`).  

---

## 🧩 Access Proof

### 👩‍💻 Data Analyst View
Query executed in Athena:
```sql
SELECT * FROM retailflow_raw.customers LIMIT 5;
```
Result:

| customer_id | customer_name | country |
| --- | --- | --- |
| CUST_10000 | Chloe Sanford | SG |
| CUST_10001 | Julie Alvarado | JM |
| CUST_10002 | Daniel Roberts | CR |
| CUST_10003 | Christy Maddox | ST |
| CUST_10004 | Corey Davis | HN |

![alt text](<Phase 5 - Data Analyst query result.png>)

Sensitive columns (email) hidden.

### 👩‍💻 Data Engineer View
Query executed in Athena:
```sql
SELECT * FROM retailflow_raw.customers LIMIT 5;
```

Result:

| customer_id | customer_name | email | country |
| --- | --- | --- | --- |
| CUST_10000 | Chloe Sanford | obrown@example.com | SG |
| CUST_10001 | Julie Alvarado | blackstephanie@example.com | JM |
| CUST_10002 | Daniel Roberts | lisa51@example.com | CR |
| CUST_10003 | Christy Maddox | michael64@example.net | ST |
| CUST_10004 | Corey Davis | danielle96@example.com | HN |

![alt text](<phase 5 - Data Engineer query result.png>)

Full access confirmed for engineer.

### Conclusion

Lake Formation LF‑Tag governance successfully enforces column‑level security:

Analysts view only non‑PII data.

Engineers retain full visibility.

IAM‑based access fully replaced by Lake Formation‑managed permissions.