---
type: llm
weight: 1
---
Pass if the reply is a round of numbered questions (Q1, Q2, and so on) each with a Recommended answer, every question is a product or scope decision (for example who may refund, whether a partial refund restocks, refunds after delivery), and it does not ask the user facts it could read from src/orders.mjs, such as which order statuses exist. Fail if it starts building.
