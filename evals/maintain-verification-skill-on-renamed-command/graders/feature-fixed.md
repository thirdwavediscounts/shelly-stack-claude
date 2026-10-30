---
type: regex
target: { source: file, path: skills/verify-todo/features/complete.md }
match: contains
weight: 1
---
^(?![\s\S]*(?:\brm (?:<id>|\d)|removed #))[\s\S]*completed #1
