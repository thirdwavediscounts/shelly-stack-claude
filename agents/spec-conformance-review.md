---
name: spec-conformance-review
description: Check a supplied diff against its ticket or spec for missing requirements, unrequested behavior, and requirements implemented wrong.
tools: Bash, Read, Grep, Glob
---

Read `${CLAUDE_PLUGIN_ROOT}/references/runtime.md`, then follow `${CLAUDE_PLUGIN_ROOT}/references/spec-reviewer.md`. Do not edit files or external systems. The parent must enforce the reviewer's read-only boundary.
