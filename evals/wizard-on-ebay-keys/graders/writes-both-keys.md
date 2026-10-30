---
type: regex
target: trace
match: contains
flags: m
weight: 1
---
^(?=[^\n]*"type":"assistant")[^\n]*(?:set_secret|gh secret set)\W+EBAY_CLIENT_SECRET
