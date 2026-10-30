---
type: llm
focus: { source: file, path: src/payments.ts }
weight: 1
---
Pass if refund takes order ids and user ids as distinct types (branded or wrapped, possibly imported from another module) so they cannot be swapped, and works on an order row that was parsed into a typed value instead of the raw any from getOrderRow. Fail if refund takes plain string ids and reads fields off the any row.
