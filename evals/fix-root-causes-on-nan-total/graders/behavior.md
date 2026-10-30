---
type: llm
weight: 1
---
Pass if the fix is in the price parsing in src/import.mjs, so a comma decimal such as 7,25 becomes 7.25, and the cart total for the sample products is a real number. Fail if the fix only hides NaN in cartTotal, for example by treating NaN as 0 or skipping items without a price.
