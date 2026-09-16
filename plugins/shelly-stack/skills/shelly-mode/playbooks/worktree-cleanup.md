### Worktree and simulator cleanup

**You own the disk and the safety gate.** Prune merged or abandoned git worktrees and stale iOS simulators to reclaim space. Deletion is irreversible, so every step guards against deleting something in use or holding uncommitted work.

1. Snapshot and audit. Record `df -h /`, resolve `<shelly-mode-skill-dir>` from the active skill's absolute `SKILL.md` path, then run `bash <shelly-mode-skill-dir>/scripts/worktree-audit.sh <repo-path>` (principle-build-the-lever). It reads paths from `git worktree list`, never hand-typed, and classifies size, age, merge state, uncommitted work, remote state, and PR state. If `PR_CHECK` is not `verified`, hold every candidate as `review-unverified-pr`; never propose deletion from an audit that could not verify open PRs.
2. The bucket is advice, not permission. Use native `list_threads` and `read_thread` when available to identify pinned, running, or recently active tasks in this project. Cross-check every candidate against those task contexts; the native task record wins over the script's suggestion.
3. Verify usage before deleting. For anything you doubt, inspect only the matching Codex task summaries and recent turns. Do not scan unrelated local session files. A pinned or running task may own sibling worktrees that do not appear in its title, so hold every path linked from its task context.
4. Separate audit from cleanup. A request such as "what's using my disk" is read-only: report the inventory and stop. For a cleanup request, show the exact worktree paths, simulator IDs, runtime IDs, or cache directories proposed for deletion and obtain explicit confirmation of that exact set before running a destructive command.
5. Treat every dirty worktree as user work. `wip:N` and `scratch:N` both require the file list and diff or status evidence. Never call untracked files throwaway. A clean or merged classification is evidence for the proposal, not permission to delete.
6. Delete only the confirmed set. Revalidate each worktree path against `git worktree list` immediately before `git worktree remove --force <exact-path>`. If ignored artifacts leave a directory behind, ask again before removing that exact directory. Run `git worktree prune`, then confirm with `df -h /` and a fresh list.
7. Treat simulators, runtimes, DerivedData, DeviceSupport, and package caches as separate destructive target classes. Inventory them first and delete only the exact IDs or directories the user confirmed; never turn a broad disk-usage question into `delete all` or cache clearing.

This is the one playbook that deletes user state with no code review to catch a slip, so the gates above are the review.

**Reply:** `df -h /` before and after with space reclaimed, the worktrees pruned, and a one-line reason for each held back (in-use by which chat, or uncommitted work).
