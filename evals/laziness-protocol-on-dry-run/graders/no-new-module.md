---
type: regex
target: files
match: not_contains
flags: m
weight: 1
---
^(?!\.git/|test/|scripts/cleanup\.mjs$|package\.json$)[^\n]*\.(?:mjs|js|cjs|json|ts)$
