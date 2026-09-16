---
name: principle-prove-it-works
description: Apply after completing a task, before declaring done. Verify against
  the real artifact (run the feature, read the actual value, inspect the diff), not
  a proxy, self-report, or 'it compiles.'
---

> **Codex runtime:** Follow the [native runtime contract](../shelly-mode/references/codex-runtime.md) for model selection, subagents, planning, review, waits, and Codex paths.

# Prove It Works

Verify every task output by checking the real thing directly. Do not infer from proxies, self-reports, or "it compiles."

**Why:** Unverified work has unknown correctness. Indirect verification (file mtimes, output freshness, agent self-reports, cached screenshots) feels cheaper than direct observation. Acting on a wrong inference costs far more than checking the source.

**Pattern:** After completing any task, ask: "how do I prove this actually works?"

Check the real thing, not a proxy:
- Check process liveness directly, not indirectly through derived state
- Read the actual value, not a cached or derived representation
- When verification fails, suspect the observation method before suspecting the system

Code and features:
1. Build it (necessary but not sufficient)
2. Run it and exercise the actual feature path
3. Check the full chain: does data flow from input to output?
4. For integrations, test the full communication path end-to-end

Delegation: trust artifacts, not self-reports.
When verifying delegated work, inspect the actual output artifact (git diff, file contents, runtime behavior), not the delegate's summary.

## Script the check when you can

The strongest proof is a deterministic check that reruns the same comparison. When file edits are authorized, add the smallest useful script and run it. For a read-only review or diagnosis, use an existing test or an inline, stdout-only command. If proof requires a new repository file, propose it instead of changing the repo.

Keep authorized artifacts visible for the human. Commit one only when the current request explicitly authorizes commits and the trail must remain auditable later. Most work needs verification evidence, not a new commit.
