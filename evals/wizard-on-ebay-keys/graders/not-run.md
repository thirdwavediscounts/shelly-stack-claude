---
type: regex
target: trace
match: not_contains
flags: m
weight: 1
---
^(?=[^\n]*"type":"assistant")[^\n]*"command":"(?:(?:ba)?sh |\./)?scripts/wizards/[\w.-]+\.sh(?:"| )
