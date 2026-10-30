---
type: llm
weight: 1
---
Pass if src/report.mjs no longer imports from test/, and the agent added a check that runs from npm test, a lint, or a script and fails when any file in src/ imports from test/, and showed that check failing on the old code or a planted violation. Fail if the only guard is a note in CLAUDE.md, a README, or a comment.
