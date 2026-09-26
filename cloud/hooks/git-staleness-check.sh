#!/usr/bin/env bash
# SessionStart hook: report how far this checkout is behind origin/main.
#
# Claude has no other way to learn this -- the git block in its system prompt
# shows branch, status, and recent commits, but not distance from the remote.
# With three devs pushing to one repo, local checkouts and worktrees go stale
# fast, and shipping a stale base silently reverts other people's merged work
# (incident 2026-08-11: a deploy 148 commits behind main wiped ~12 features).
#
# Always exits 0 -- a session must never fail to start because of this check.

set -u

# Not a git repo (or no remote): nothing to say.
git rev-parse --git-dir >/dev/null 2>&1 || exit 0
git remote get-url origin >/dev/null 2>&1 || exit 0

git fetch origin --quiet 2>/dev/null || exit 0

behind=$(git rev-list --count HEAD..origin/main 2>/dev/null) || exit 0
[ "${behind:-0}" -gt 0 ] || exit 0

branch=$(git branch --show-current 2>/dev/null || echo "detached")

printf '{"systemMessage":"%s commits behind origin/main (on %s) - rebase before editing or deploying","hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"This checkout is %s commits behind origin/main (current branch: %s). Per the team guidelines, rebase onto origin/main before editing or deploying - shipping a stale base reverts other people'"'"'s merged work. Tell the user before starting substantive work."}}' \
  "$behind" "$branch" "$behind" "$branch"

exit 0
