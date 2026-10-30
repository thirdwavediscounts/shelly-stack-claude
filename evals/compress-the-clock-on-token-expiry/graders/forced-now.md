---
type: llm
weight: 1
---
Pass if, in this session, the agent forced the expiry on a copy of state/tokens.json (for example by back-dating expires_at) and ran getAccessToken against that copy, and the reply reports the result now instead of planning to check after tomorrow 9am.
