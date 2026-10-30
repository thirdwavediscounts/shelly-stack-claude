---
type: llm
weight: 1
---
Pass if a price becomes a value that carries its currency (an amount plus a currency) through products, formatPrice, and cartTotal, formatPrice prints the right symbol for EUR, and a cart with mixed currencies is rejected. Fail if the change only adds an optional currency argument to formatPrice while prices stay bare numbers.
