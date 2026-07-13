# Athena Cost Comparison

## Objective

The objective of this exercise is to demonstrate the impact of **partition pruning** in Amazon Athena. Since Athena pricing is based on the amount of data scanned, using partition filters significantly reduces query cost and improves query performance.

---

# Test 1 – order_items Table

## Query 1: Without Partition Pruning

### SQL

```sql
SELECT *
FROM order_items;
```

### Result

| Metric | Value |
|---------|---------|
| Query Runtime | 902 ms |
| Data Scanned | **6.36 MB** |

### Screenshot

> **Insert Screenshot:** `order_items unpurned athena query.png`
![alt text](<order_items unpruned athena query.png>)

---

## Query 2: With Partition Pruning

### SQL

```sql
SELECT order_id
FROM order_items
WHERE dt = '2026-07-09';
```

### Result

| Metric | Value |
|---------|---------|
| Query Runtime | 519 ms |
| Data Scanned | **1.24 MB** |

### Screenshot

> **Insert Screenshot:** `order_items purned athena query.png`
![alt text](<order_items pruned athena query.png>)

---

## Comparison

| Query | Data Scanned |
|---------|-------------:|
| Without Partition Filter | **6.36 MB** |
| With Partition Filter | **1.24 MB** |

### Observation

Using the partition column (`dt`) reduced the amount of data scanned from **6.36 MB** to **1.24 MB**, which is approximately an **80% reduction**.

---

# Test 2 – orders Table

## Query 1: Without Partition Pruning

### SQL

```sql
SELECT *
FROM orders;
```

### Result

| Metric | Value |
|---------|---------|
| Query Runtime | 1044 ms |
| Data Scanned | **5.12 MB** |

### Screenshot

> **Insert Screenshot:** `orders - unpruned athena query.png`

![alt text](<orders unpruned-1.png>)

## Query 2: With Partition Pruning

### SQL

```sql
SELECT order_id
FROM orders
WHERE dt = '2026-07-09';
```

### Result

| Metric | Value |
|---------|---------|
| Query Runtime | 451 ms |
| Data Scanned | **618.23 KB** |

### Screenshot

> **Insert Screenshot:** `orders - pruned athena query.png`
![alt text](<orders pruned.png>)

---

## Comparison

| Query | Data Scanned |
|---------|-------------:|
| Without Partition Filter | **5.12 MB** |
| With Partition Filter | **618.23 KB** |

### Observation

Using the partition filter reduced the amount of data scanned from **5.12 MB** to **618.23 KB**, which is approximately an **88% reduction**.

---

# Overall Cost Comparison

| Table | Unpruned Query | Bytes Scanned | Pruned Query | Bytes Scanned | Reduction |
|--------|----------------|--------------:|--------------|--------------:|----------:|
| order_items | `SELECT * FROM order_items;` | **6.36 MB** | `SELECT order_id FROM order_items WHERE dt='2026-07-09';` | **1.24 MB** | **≈80%** |
| orders | `SELECT * FROM orders;` | **5.12 MB** | `SELECT order_id FROM orders WHERE dt='2026-07-09';` | **618.23 KB** | **≈88%** |

---

# Conclusion

This comparison demonstrates the effectiveness of **partition pruning** in Amazon Athena.

- Athena scans only the required partition when the query includes the partition column (`dt`).
- Less data scanned directly translates into **lower query cost** because Athena charges based on the amount of data processed.
- Partition pruning also improves query execution time by avoiding unnecessary file scans.
- Organizing datasets using partitioned S3 folders and filtering on partition columns is a recommended best practice for building scalable and cost-efficient data lakes.

## Best Practice

Always include partition columns (such as `dt`, `year`, `month`, or `region`) in Athena queries whenever possible to minimize data scanned and optimize both performance and cost.