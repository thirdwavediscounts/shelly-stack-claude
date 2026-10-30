---
type: llm
weight: 1
---
Pass if the explanation walks checkout in order (cart subtotal, tax, stock reserved, payment charged), says which file holds each step, and points out that stock is reserved before the charge, so a failed charge leaves stock reserved. It should also note that an unknown state gets zero tax.
