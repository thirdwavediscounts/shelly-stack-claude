### Shipping

**You own what lands. Verify each PR independently, land only the verified run from the root, then merge it bottom-up one PR at a time.** For "land the stack", "ship it", "merge it", "enable merge when ready", or the second half of a stack that **Babysit** already drove to green. Shipping runs only on those words. Merging is the user's explicit call, because merging usually deploys.

This is the half after `playbooks/babysit.md`. Babysit makes a stack mergeable. Shipping decides what is actually safe to merge and lands it through `gh`. Green is not safe, and the gap between those two words is where this playbook lives.

1. **Verify every PR independently before merging anything.** One fresh subagent per PR, not batched, remote (`isolation: "remote"`) when available, local otherwise, each exercising the real surface (the project's verification skill as the change demands) against parent versus head. Each returns `PASS`, `PASS+NOTES` or `FAIL` and posts that verdict on its own PR so the record outlives the chat. Safe means a verdict from an agent that did not write the code. CI green is not a verdict, and an approving bot review is not a verdict.
2. **Land only the contiguous verified run rooted at the bottom.** Walk up from the lowest unmerged PR and stop at the first one without a passing verdict, where both `PASS` and `PASS+NOTES` pass. A verified PR sitting above an unverified one is not landable, because merging it would pull the gap in underneath it. Report the ceiling as a PR number and say what breaks the chain.
3. **Re-check that the verdicts still describe the code.** A rebase rewrites every SHA above it and silently invalidates every verdict without touching a single check. Compare `git patch-id` at the verdict SHA against the current head before trusting an older verdict, and re-verify anything that actually drifted. Twenty-one verdicts went stale this way in one run with no signal at all.
4. **Merge bottom-up, one PR at a time.** Record the lowest PR's `headRefOid`, confirm it reads `READY` per the babysit verdict, then merge it.
   ```bash
   gh pr merge <n> --squash --delete-branch
   ```
   GitHub retargets the children to `main` when the parent merges with its branch deleted. Confirm the retarget with `gh pr view <child> --json baseRefName` before you touch the next PR. The child branch still carries the parent's original commits, so replay only the child's own commits onto trunk before its status means anything.
   ```bash
   git fetch origin && git rebase --onto origin/main <parent headRefOid> <child-branch> && git push --force-with-lease
   ```
   Step 3 then decides whether the child's verdict still stands. A conflict here is a real conflict with trunk. Resolve it on the branch, then treat the PR as drifted and re-verify. Never rewrite a branch you do not own. Read the child's status again, wait for its checks, and merge it the same way. Repeat to the ceiling.
5. **Arm `--auto` only when the user asked for merge-when-ready, and only on the PR that targets `main`.** A child PR targets its parent branch, which has no protection, so `gh pr merge --auto` merges it into the parent at once and collapses the stack into itself. Arm the root, wait for the merge, then rebase and arm the next PR. If a previous agent armed a child, disarm with `gh pr merge <n> --disable-auto` and confirm with `gh pr view <n> --json autoMergeRequest` that the field is back off.
6. **While landing, touch only the PR being landed.** No speculative pushes above it, and no rebase of anything but the next PR in line. Independent work gets rebased onto `main` and shipped on its own.
7. **Poll between merges, and diagnose before mutating.** Hold the poll under `/loop` in Claude Code. Codex uses a native wait or a heartbeat automation. Rearm it after every merge and every verdict you act on, until the ceiling lands. Report each merge and the new ceiling. If a merge is refused or a check stalls, read `mergeStateStatus` and the failing check before pushing anything, because a stalled check and a broken stack look identical from the outside.
8. **Stop at the ceiling.** When the verified run is merged, report what landed, what the next unverified PR is, and what verifying it would take. Extending the run is a new pass through step 1, not a judgment call you make at 3am.

**Reply:** the verified run and its ceiling, each PR's verdict and who produced it, what you merged or armed and how you confirmed it, what landed, and what the next gap needs.
