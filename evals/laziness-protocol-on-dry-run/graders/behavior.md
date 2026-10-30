---
type: llm
focus: { source: file, path: scripts/cleanup.mjs }
weight: 1
---
Pass if the dry-run support is small: a flag check and a print in place of the delete, a few lines added. Fail if it adds a class, an options or argument-parsing framework, or a config loader.
