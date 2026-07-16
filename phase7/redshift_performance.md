# Redshift Performance Analysis

## Task 41 – EXPLAIN Plan

### Query

```sql
EXPLAIN
SELECT
    p.category,
    SUM(f.line_total) AS revenue
FROM retailflow.fact_order_items f
JOIN retailflow.dim_product p
    ON f.product_id = p.product_id
GROUP BY p.category;
```

---

## Execution Plan

```
XN HashAggregate
  -> XN Hash Join DS_DIST_NONE
       Hash Cond:
       (fact_order_items.product_id = dim_product.product_id)

       -> XN Seq Scan on fact_order_items

       -> XN Hash
            -> XN Seq Scan on dim_product
```

---

# Explanation

## 1. Sequential Scan on fact_order_items

Redshift performs a sequential scan on the `fact_order_items` table.

Since this is the largest table in the star schema, every row is scanned to retrieve:

- product_id
- line_total

This scan provides the transactional data required for revenue calculation.

---

## 2. Sequential Scan on dim_product

The optimizer performs a sequential scan on the `dim_product` table.

The table is relatively small (dimension table), so a sequential scan is more efficient than using an index.

The required columns are:

- product_id
- category

---

## 3. Hash Join

The execution plan uses a **Hash Join**.

```
Hash Cond:
fact_order_items.product_id =
dim_product.product_id
```

Redshift first creates an in-memory hash table from the smaller `dim_product` table.

Each row from `fact_order_items` is then matched against this hash table using `product_id`.

This is the preferred join strategy for large fact tables joined with smaller dimension tables.

---

## 4. DS_DIST_NONE

The execution plan shows:

```
DS_DIST_NONE
```

This indicates that no data redistribution was required during the join.

This happens because both tables share the same distribution key:

- `product_id`

Using the same `DISTKEY` minimizes network traffic and improves join performance.

---

## 5. Hash Aggregate

Finally, Redshift performs a **Hash Aggregate** operation.

```
GROUP BY category
```

The aggregation computes:

```sql
SUM(line_total)
```

for each product category.

The final output contains:

- Category
- Total Revenue

---

# Performance Observations

- Sequential scan is efficient for large analytical workloads.
- Hash Join is the optimal join strategy for a star schema.
- Using `product_id` as the `DISTKEY` avoids data movement.
- Aggregation is performed after the join to calculate revenue by category.
- The execution plan indicates an optimized query with no unnecessary redistribution.

---

# Conclusion

The query follows a typical star-schema execution pattern in Amazon Redshift:

1. Scan the fact table (`fact_order_items`).
2. Scan the dimension table (`dim_product`).
3. Perform an in-memory Hash Join on `product_id`.
4. Aggregate revenue by `category`.
5. Return the grouped revenue results.

The presence of `DS_DIST_NONE` confirms that the distribution style is well-designed, reducing network overhead and improving query performance.