---
name: thermo-nuclear-code-quality-review
description: Run a strict maintainability audit of a diff for structural regressions,
  unnecessary layers, branching, and unclear type boundaries. Use for an explicitly
  requested thermonuclear or deep code quality review.
---

# Review maintainability

Read the [runtime contract](../../references/runtime.md). Review the supplied change without editing it. Prefer a few findings that remove substantial complexity over cosmetic feedback.

## Gather evidence

Resolve the intended base and inspect the branch diff, scoped uncommitted changes, and relevant complete files. Include callers when a changed boundary affects them. Do not gather unrelated chat history. If independent review is required, use the [reviewer prompt](../../references/maintainability-reviewer.md) through the runtime's enforced read-only branch.

## Rubric

- Look for a different data structure or ownership boundary that eliminates branches, modes, duplicated state, or entire helper layers while preserving behavior.
- Flag a file crossing 1,000 lines when the new material has a coherent separate responsibility. Size is evidence to inspect, not a reason to split cohesive code mechanically.
- Trace new special cases and scattered conditionals to the missing model. Suggest a state machine, typed variant, table, or direct flow only when it reduces reader effort.
- Reject thin wrappers, identity helpers, and generic mechanisms that hide a simple operation. Reuse the existing canonical helper when it fits.
- Keep feature logic in the layer that owns it. Show the caller affected by a leaking boundary.
- Inspect unnecessary optionality, casts, and duplicate type definitions. Keep external input `unknown` until validated. Do not remove real boundary checks as cleanup.
- Flag avoidable sequential work only when independence is established. Identify partial updates that violate a real atomicity requirement.
- Prefer deletion and direct code to moving the same complexity into more files.

## Findings

Order findings by structural regressions, concrete simplifications, branching growth, boundary and type problems, decomposition, and readability. Each finding names the file and line, the actual cost, and a specific remedy. Explain why the simpler structure preserves behavior. Label untested alternatives as proposals.

A passing test does not settle maintainability. A plausible redesign is also not proof that the current change must be blocked. Recommend changes when the evidence shows a regression or a clear reduction in complexity. Do not demand unrelated refactors.

Return the actionable findings and verification gaps, or state that no actionable maintainability findings remain. Applying fixes is a separate authorized step.
