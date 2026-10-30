---
type: regex
target: trace
match: contains
flags: m
weight: 1
---
^(?=[^\n]*"type":"assistant")[^\n]*(?:log\.sh|decision-log-template\.tsv|ts\\tphase\\tdecision\\tby\\twhy\\tevidence\\tresult)
