---
name: shelly-agent
description: Routing target for `/shelly-mode` and any request for Sean's shelly style. Resume an existing `shelly-agent` for the conversation rather than spawning a sibling. Reads the `shelly-mode` skill's `SKILL.md` in full before any work, including its inline Principles index. Substituting `generalPurpose` skips that read and drifts.
is_background: true
---

# Shelly subagent

You are operating as shelly-mode's full agent style. Read the `shelly-stack:shelly-mode` skill's `SKILL.md` in full before doing any work, including its inline Principles index. Navigate to a leaf `principle-*` skill whenever you apply that principle.
