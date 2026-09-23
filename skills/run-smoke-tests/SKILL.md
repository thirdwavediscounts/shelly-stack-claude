---
name: run-smoke-tests
description: Run the repository's end-to-end smoke suite, debug failures, and verify fixes. Use when smoke or end-to-end verification is needed before or after a change, whatever framework the repository uses.
disable-model-invocation: true
---

Read the [runtime contract](../../references/runtime.md) before using this skill.

# Run smoke tests

## Workflow

1. Build prerequisites for the target app.
2. Run the relevant smoke suite or a focused test file.
3. If failing, inspect traces/logs and isolate the root cause.
4. Apply a minimal fix and rerun until stable.

## Commands

Read the repository scripts and verification skill to find the smoke command, launch prerequisites, and supported file filter. Do not assume `npm run smoketest` exists. Reuse a passing result at the same source state.

## Guardrails

- Prefer deterministic waits and assertions over brittle timeouts.
- Repeat a passing check only when changed code or observed flakiness justifies it.
- Quarantine tests only when explicitly requested and documented.

## Output

- Test results summary
- Root cause and fix
- Remaining flake risk (if any)
