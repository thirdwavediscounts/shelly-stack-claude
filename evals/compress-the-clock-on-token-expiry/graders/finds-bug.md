---
type: llm
weight: 1
---
Pass if the reply says the refresh does not fire on an expired token because expires_at is an ISO string compared with the number Date.now(), so the comparison is always false.
