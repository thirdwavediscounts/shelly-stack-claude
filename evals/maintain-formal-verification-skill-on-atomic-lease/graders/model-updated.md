---
type: llm
focus: { source: file, path: check/lease-model.mjs }
weight: 1
---
Pass if the model treats acquire as one atomic step, a single set-if-absent, instead of a separate read and then write.
