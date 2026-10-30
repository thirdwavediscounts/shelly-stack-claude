---
type: regex
target: { source: file, path: .git/logs/HEAD }
match: contains
weight: 1
---
(?:\tcommit: [^\n]*\n[\s\S]*?){4}
