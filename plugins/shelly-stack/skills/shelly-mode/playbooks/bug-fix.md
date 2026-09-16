### Bug fix

**You own this task. Plan, review, verify.** Delegate investigation and the fix to subagents, stay in the lead.

Be scientific. Every shipped line traces to runtime evidence. Belt-and-suspenders that "might help" is a hypothesis, not a fix. It does not ship. When evidence refutes a hypothesis, revert what it motivated. The smallest change the evidence justifies ships, nothing more.

1. Reproduce it yourself on the matching surface via the verification skill (Non-negotiables). Don't hand the repro to the user. You drive the instrumented runtime. Ask the user only with a stated, specific reason the verification surface cannot reach the target, and only after driving it as far as it goes. Won't reproduce directly, force it: synthesize the trigger, tighten conditions, or instrument until it fires.
2. Binary-search the cause. Form the candidate hypotheses, then rule them out until one survives. Seed them with `how` over the affected subsystem and the **[why](../references/routed/why/workflow.md)** skill for regression history. Each pass, take the split that cuts the most remaining problem space, get runtime evidence, eliminate. When program state is unclear, add instrumentation or logging and read it as the code runs. Don't guess. Drive a long or stubborn hunt with the native runtime contract's current-turn continuation rules. Confirm the surviving *mechanism* with runtime evidence before the step-3 architect/interrogate fan-out.
3. Plan the fix. If it crosses a function boundary, `architect` first. Delegate implementation to a subagent using the configured `bug-fix` `<model>@<reasoning_effort>` pair or the native runtime fallback with a specific scope; review the diff.
4. Verify on the same surface; the original repro now passes. "Inconclusive" or wrong-surface is not a pass; flag it. Unit tests show branch behavior, not bug absence.
5. Keep failing-then-passing evidence through the **[tdd](../references/routed/tdd/workflow.md)** and **[sequence-verifiable-units](../references/routed/principle-sequence-verifiable-units/workflow.md)** skills when the bug has a cheap local test path. If commits are explicitly authorized, place the failing repro before the fix in history; otherwise leave the verified diff uncommitted.
6. If the current request explicitly authorizes PR creation and pushing, run **Opening a PR**. Otherwise stop with verified local changes.

Investigation fans out `how` + `why` as parallel subagents.

**Reply:** what was broken, root cause, fix, how you verified. Paste failing-then-passing repro output verbatim.
