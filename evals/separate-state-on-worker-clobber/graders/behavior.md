---
type: llm
weight: 1
---
Pass if each worker now writes its own state (its own file or another write target only it owns) and run-both.mjs, or its updated version, shows both last-run values kept. Fail if the fix is a lock, queue, or retry around the shared state.json while both workers still write it, unless the reply shows why one shared file is required.
