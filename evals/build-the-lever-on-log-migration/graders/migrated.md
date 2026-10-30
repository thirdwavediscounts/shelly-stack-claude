---
type: regex
target: { source: file, path: src/jobs/job30.mjs }
match: contains
weight: 1
---
^(?![\s\S]*oldLog)[\s\S]*log\.info
