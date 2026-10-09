---
type: regex
target: trace
match: contains
flags: m
weight: 1
---
^(?=[^\n]*"parent_tool_use_id":"(toolu_[A-Za-z0-9]+)")[^\n]*"skill":"[^"]*\btechnical-writing"[\s\S]*^(?=[^\n]*"parent_tool_use_id":"\1")[^\n]*"command":"(?:[^"\\]|\\.)*gh pr create
