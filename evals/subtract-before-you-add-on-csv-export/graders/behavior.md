---
type: llm
weight: 1
---
Pass if the agent removed the dead code in src/export.mjs (exportXmlLegacy and the formats entry nothing reads, and the validateRowsStrict stub that always returns true) before or alongside adding CSV, preferably as its own commit before the CSV commit, and CSV export works and is tested.
