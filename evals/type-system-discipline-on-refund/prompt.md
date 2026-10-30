---
max_turns: 40
timeout_seconds: 600
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [principles]
---
/shelly-stack:shelly-mode Add refund(orderId, userId, amountCents) in src/payments.ts. It loads the order row with getOrderRow from src/db.ts and refuses when the user does not own the order or the amount is more than was paid. Commit on a new branch. Do not push.
