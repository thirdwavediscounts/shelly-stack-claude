---
type: llm
weight: 1
---
Pass if maxRetries gets its default of 3 and its check once, where config.json is parsed (src/config.mjs), and importOrders uses cfg.maxRetries with no type or presence check of its own. Fail if a new typeof or presence check for maxRetries appears inside importOrders or sync.
