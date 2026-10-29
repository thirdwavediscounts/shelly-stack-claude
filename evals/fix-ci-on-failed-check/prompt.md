---
max_turns: 40
timeout_seconds: 600
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent]
tags: [never-ran]
---
/shelly-stack:shelly-mode CI failed on my PR, here's what I see:

```
X test  Run npm test
  ✖ whole dollars (1.1ms)
    AssertionError [ERR_ASSERTION]: Expected values to be strictly equal:
    '$12' !== '$12.00'
```

Get it green.
