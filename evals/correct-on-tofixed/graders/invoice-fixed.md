---
type: regex
target: { source: file, path: src/invoice.mjs }
match: contains
weight: 1
---
^(?![\s\S]*toFixed)[\s\S]*formatPrice
