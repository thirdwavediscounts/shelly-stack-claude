---
type: regex
target: trace
match: contains
flags: m
weight: 1
---
^(?=[^\n]*"type":"assistant")[^\n]*getAccessToken\((?!statePath|\))
