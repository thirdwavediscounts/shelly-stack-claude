---
type: llm
focus: files
weight: 1
---
The input is the list of file paths the run created or changed (paths under .git/ are git's own bookkeeping). Pass if the list includes a test, lint config, or script outside .git/ that could hold a check, not only CLAUDE.md or other docs.
