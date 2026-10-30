---
type: regex
target: { source: file, path: src/export.mjs }
match: contains
flags: i
weight: 1
---
^(?![\s\S]*(?:exportXmlLegacy|validateRowsStrict))[\s\S]*csv
