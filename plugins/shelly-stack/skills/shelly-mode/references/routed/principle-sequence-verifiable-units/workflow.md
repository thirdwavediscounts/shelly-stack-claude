# Sequence work into verifiable units

Order work as a sequence of small units, each ending in a state you can check, and don't advance until the current one is green.

**Why:** A break caught at the unit that caused it is cheap to localize. A break caught after a batch is buried, and you have already built further on a broken base. Sequencing those same units into a delivery a reviewer can replay turns "trust me" into "watch it go red, then green."

**Execution.** In a sweep, migration, or any run of similar edits, verify each change before starting the next. Never batch edits and verify once at the end. Compare with the real baseline using read-only Git inspection. Rebase only when the current request explicitly authorizes history changes. When a lever does the edits, run its per-unit check.

**Delivery.** When commits or PRs are explicitly authorized, order them so each verified unit stands alone, such as a failing test followed by its fix. Without that authority, preserve the same verified unit order in the working-tree diff and report the evidence; do not create or rewrite history.

**Pattern:**
- Pick the smallest unit that ends in a check: an edit plus its test, or a commit that stands alone.
- Verify before advancing. Red to green per unit, never deferred to a final batch.
- Order the units so the sequence builds confidence on its own, for you while executing and for a reviewer reading the stack.

The sequencing complement to the **[prove-it-works](../principle-prove-it-works/workflow.md)** principle skill, which keeps each check real, and the **[build-the-lever](../principle-build-the-lever/workflow.md)** principle skill, which makes the per-unit check cheap.
