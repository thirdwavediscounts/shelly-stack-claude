### Session pickup

**You own the resume point. Read the prior trail, don't redo it.** For "take over this", "resume this conversation", "continue from <transcript path>", "you're taking over", "pick up where X left off", or a pushed branch you're meant to continue.

1. Locate the prior trail through the current conversation, native `list_threads` and `read_thread` when available, a provided task link, an exact user-supplied session path, or a pushed branch. Read summaries and recent turns first, then inspect only the decision points needed to resume. Never discover or scan unrelated `~/.codex/sessions/` records. Reduce a long trail in a read-only subagent so bulk history stays out of the parent context (the **[principle-guard-the-context-window](../references/routed/principle-guard-the-context-window/workflow.md)** skill).
2. Reconstruct operational state. The branch and worktree, what already landed (`git log`, `git diff` against the base), the open todos, the decisions made. The prior trail is authoritative input. Resist the bias to re-derive it.
3. Diff done vs pending. Compare what shipped against what was planned and name the resume point. Do not redo completed work or re-run the prior repro; step 5 checks the inherited claims on the artifact.
4. Route the remaining work to the matching playbook and pick the verdict: continue the execution, ship a finished recommendation, ratify or override a prior conclusion, or postmortem a failed run. The pickup playbook ends here. The routed playbook owns the rest.
5. Verify the inherited claims against the original goal on the real artifact (the **[principle-prove-it-works](../references/routed/principle-prove-it-works/workflow.md)** skill). A passing prior self-report is not the proof.

**Reply:** where the prior agent stopped, what you inherited vs redid (ideally nothing redone), the resume point, and the outcome.
