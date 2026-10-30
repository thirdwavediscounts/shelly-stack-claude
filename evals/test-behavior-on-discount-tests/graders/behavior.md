---
type: llm
weight: 1
---
Pass if the new tests call applyDiscount with concrete inputs and compare against literal expected totals (for example applyDiscount(200, 'SAVE10') is 180), cover an unknown code returning the full total, and do not assert on internal helpers such as lookupRate being called. The existing spy test should be rewritten or removed, or flagged in the reply.
