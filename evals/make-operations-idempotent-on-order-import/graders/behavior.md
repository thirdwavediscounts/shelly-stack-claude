---
type: llm
weight: 1
---
Pass if rerunning the import after a crash at any point leaves each order in data/orders.json exactly once (for example an upsert keyed by order id, or a reconcile step that skips orders already present), and the agent proved it by running the import after a simulated crash (crashAfterWrite) and checking each order appears once.
