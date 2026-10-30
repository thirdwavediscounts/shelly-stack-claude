---
type: llm
focus: { source: file, path: src/importOrders.mjs }
weight: 1
---
Pass if rerunning importOrders after a crash at any point, including right after it writes data/orders.json and before it moves the batch file, leaves each order in data/orders.json exactly once, for example by upserting by order id or skipping ids already present.
