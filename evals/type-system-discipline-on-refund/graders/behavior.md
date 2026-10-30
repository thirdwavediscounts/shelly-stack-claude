---
type: llm
weight: 1
---
Pass if order ids and user ids get distinct types (branded or wrapped) so they cannot be swapped, the JSON order row is parsed into a typed value at the boundary instead of used as any, and refund uses those types. Fail if refund takes plain string ids and trusts the any row.
