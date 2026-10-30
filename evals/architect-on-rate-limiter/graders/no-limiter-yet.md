---
type: regex
target: { source: file, path: src/api.mjs }
match: not_contains
weight: 1
---
429|clientId
