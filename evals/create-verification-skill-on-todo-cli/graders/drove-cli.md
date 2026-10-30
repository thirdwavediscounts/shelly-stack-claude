---
type: regex
target: trace
match: contains
flags: m
weight: 1
---
^(?=[^\n]*"type":"assistant")[^\n]*"command":"(?:[^"\\]|\\.)*?(?:todo\.mjs|control-todo|verify-todo)(?:[^"\\]|\\.)*?\b(?:add|done)\b
