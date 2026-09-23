### Session pickup

**You own the resume point. Read the prior trail, don't redo it.** For "take over this", "resume this conversation", "continue from <transcript path>", "you're taking over", "pick up where X left off", or a pushed branch you're meant to continue.

1. Locate the prior trail. A local transcript under the workspace's `~/.claude/projects/<slug>/` directory (derive the slug from the working directory, every `/` turned into `-`; do not glob across `~/.claude/projects/*/`, that crosses workspace boundaries and reads private chats from unrelated projects), or a pushed branch. Read the metadata overview and last messages first, then scan back for the decision points. Parse a long transcript in a subagent and keep the reduced timeline in the main thread (the **principle-guard-the-context-window** skill).
2. Reconstruct operational state. The branch and worktree, what already landed (`git log`, `git diff` against the base), the open todos, the decisions made. The prior trail is authoritative for what was decided and done. Resist the bias to re-derive it. Infra facts are the exception: re-derive hosts, ssh aliases, paths, and sudo needs from the current rules files (`CLAUDE.md`, `CLAUDE.local.md`, `~/.claude/rules/`), and treat those facts in the transcript or handoff prompt as stale until confirmed.
3. Diff done vs pending. Compare what shipped against what was planned and name the resume point. Do not redo completed work or re-run the prior repro; step 5 checks the inherited claims on the artifact.
4. Route the remaining work to the matching playbook and pick the verdict: continue the execution, ship a finished recommendation, ratify or override a prior conclusion, or postmortem a failed run. The pickup playbook ends here. The routed playbook owns the rest.
5. Verify the inherited claims against the original goal on the real artifact (the **principle-prove-it-works** skill). A passing prior self-report is not the proof.

**Reply:** where the prior agent stopped, what you inherited vs redid (ideally nothing redone), the resume point, and the outcome.
