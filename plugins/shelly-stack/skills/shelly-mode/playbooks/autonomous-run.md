### Autonomous run

**You own the exit condition. Define done, then drive to it without stopping.**

1. State the exit condition as a checkable predicate before the first iteration (tests green, repro fixed, all N PRs merged, pixel-diff zero).
2. Choose the native continuation mechanism. While this task and its subagents are active, use `wait_agent` or the relevant bounded watcher. If the user explicitly asked for a recurring check or a later follow-up, use the native runtime contract's recurring-check branch. Size any available interval to when the result is worth checking again.
3. Each iteration makes the smallest change the evidence justifies and verifies it against the predicate. Commit an advancing change only when commits are authorized; otherwise keep the verified working-tree diff. Revert changes that did not help. Belt-and-suspenders that "might help" gets reverted, not left to ride.
   Sequence the work via the **[sequence-verifiable-units](../references/routed/principle-sequence-verifiable-units/workflow.md)** principle skill, verifying each unit before the next instead of batching checks at the end.
4. Mid-run discoveries are yours. Address broken skills, related bugs, flaky verifiers, review noise, tooling failures, orphaned follow-ups, and fixable drift yourself via shelly-mode. Keep out-of-band fixes in separate local changes. Open a PR only when the user explicitly authorizes PR creation. Do not park reversible work for the human or use `request_user_input`. Surface only irreversible actions, genuine product or preference calls no experiment can settle, or a real dead end. Keep the predicate as the main drive, and return to it after each side fix.
5. Checkpoint every iteration via the **[show-me-your-work](../references/routed/show-me-your-work/workflow.md)** skill, a row for what changed and whether the predicate moved.
6. Stop when the predicate is met. A plateau is not a stop, so keep going and pivot your approach to push past it. Surface a genuine dead end rather than spinning, and never relax the predicate to declare victory.

**Reply:** the exit condition, iterations run, what landed, what was discarded, final predicate state.
