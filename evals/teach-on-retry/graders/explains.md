---
type: llm
weight: 1
---
Pass if the explanation opens with a short plain definition (retry with exponential backoff and jitter), explains that only 429 and 5xx responses are retried and how the wait grows with each attempt, uses plain sentences rather than a list of functions and constants, and reads as an explanation, not a report of what the agent did.
