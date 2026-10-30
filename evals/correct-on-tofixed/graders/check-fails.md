---
type: llm
weight: 1
---
Pass if the agent added a check that runs from npm test or a script and fails when code outside src/price.mjs calls toFixed, showed it failing on a real past mistake (src/invoice.mjs, or the product or receipt commit), fixed src/invoice.mjs to use formatPrice, and the reply names the level it picked and why a higher level did not work. Fail if the only change is more text in CLAUDE.md.
