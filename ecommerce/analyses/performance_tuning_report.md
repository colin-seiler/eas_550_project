# Performance Tuning Report — Step 2.3

## Query Profiled

Query 3 (monthly revenue trends) — picked this one because it's the heaviest: a CTE feeding into window functions across two large tables joined together.

---

## Before Adding Indexes

```
WindowAgg  (cost=18448.99..24066.98 rows=95653 width=112) (actual time=135.380..157.005 rows=23 loops=1)
  ->  Sort  (actual time=135.291..143.505 rows=109909 loops=1)
        Sort Method: external merge  Disk: 3488kB
        ->  Hash Join  (actual time=26.012..88.207 rows=109909 loops=1)
              ->  Seq Scan on orderitems oi  (actual time=0.007..7.738 rows=112348 loops=1)
              ->  Seq Scan on orders o  (actual time=0.008..14.049 rows=96214 loops=1)
                    Filter: (status = 'delivered'::status_enum)
                    Rows Removed by Filter: 2949
Planning Time: 0.855 ms
Total Execution Time: 157.005 ms
```

Two things stand out here. First, both tables are doing full sequential scans — every single row gets read before filtering happens. Second, the sort spilled to disk (3488kB) because the dataset was too big to sort in memory. Total time: 157ms.

---

## Indexes Added

```sql
-- filter orders by delivery status faster
CREATE INDEX idx_orders_status ON commerce.orders(Status);

-- speed up the join between orders and orderitems
CREATE INDEX idx_orderitems_orderid ON commerce.orderitems(OrderID);

-- help with the date_trunc grouping on purchase time
CREATE INDEX idx_orders_purchasetime ON commerce.orders(OrderPurchaseTime);
```

---

## After Adding Indexes

```
WindowAgg  (cost=18403.92..24006.33 rows=95386 width=112) (actual time=127.726..148.964 rows=23 loops=1)
  ->  Sort  (actual time=127.640..135.734 rows=109909 loops=1)
        Sort Method: external merge  Disk: 3488kB
        ->  Hash Join  (actual time=25.188..83.209 rows=109909 loops=1)
              ->  Seq Scan on orderitems oi  (actual time=0.007..6.714 rows=112348 loops=1)
              ->  Seq Scan on orders o  (actual time=0.007..13.104 rows=96214 loops=1)
                    Filter: (status = 'delivered'::status_enum)
                    Rows Removed by Filter: 2949
Planning Time: 1.745 ms
Total Execution Time: 148.964 ms
```

Down to 148ms. Still sequential scans though — Postgres didn't touch the indexes.

---

## Why Postgres Ignored the Indexes

This one took me a second to understand. The query filters for `status = 'delivered'`, which sounds like a great use case for an index. But 96,214 out of 99,163 orders are delivered — that's 97% of the table. When you need almost every row anyway, jumping around the table via an index is actually slower than just reading it straight through. Postgres figured this out and skipped the indexes entirely.

The indexes would help a lot more for low-selectivity queries — like finding canceled orders (only ~3% of the table) or looking up a single order by ID.

---

## Results

| | Before | After |
|---|---|---|
| Execution time | 157ms | 148ms |
| Sort method | External merge (disk) | External merge (disk) |
| Scan type | Sequential | Sequential |

About a 6% drop in execution time, but no structural change. The bottleneck is just the volume of data — 112k order items joined to 96k orders is a lot to move around. For a reporting query like this, a materialized view or pre-aggregated summary table would probably help more than indexes.