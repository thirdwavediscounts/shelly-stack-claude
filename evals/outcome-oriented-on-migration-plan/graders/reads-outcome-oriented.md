---
type: regex
target: trace
match: contains
flags: m
weight: 1
---
^(?=[^\n]*"type":"assistant")[^\n]*"name":"(Read|Bash)"[^\n]*outcome-oriented-execution
