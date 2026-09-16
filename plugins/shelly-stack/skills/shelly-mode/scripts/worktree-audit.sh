#!/usr/bin/env bash
# Read-only worktree prune audit. Classifies every git worktree by size, merge
# state, uncommitted work, remote state, and verified PR state. Emits a table
# sorted by size with a suggested bucket. Never deletes anything; deletion stays
# a human-gated step in the playbook.
#
# Usage: worktree-audit.sh [repo-path]   (defaults to the current repo)
set -u

repo="${1:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -z "$repo" ] && { echo "not in a git repo; pass a repo path" >&2; exit 1; }
cd "$repo" || exit 1

# Main worktree is the first entry; everything else is a candidate.
main_wt=$(git worktree list --porcelain | awk '/^worktree /{print $2; exit}')

# Use the local origin/main snapshot so this audit does not mutate refs.
# Report that merge state may be stale; refreshing refs is a separate authorized action.

# Verify every dependency before treating remote PR state as evidence.
prs=$(mktemp)
pr_check=unavailable
if command -v gh >/dev/null 2>&1 \
	&& command -v jq >/dev/null 2>&1 \
	&& gh auth status >/dev/null 2>&1 \
	&& gh repo view --json nameWithOwner >/dev/null 2>&1 \
	&& gh pr list --state all --limit 1000 \
		--json number,state,headRefName > "$prs" 2>/dev/null; then
	pr_check=verified
else
	printf '%s\n' 'warn: PR state unavailable; no worktree can be classified safe' >&2
	printf '[]\n' > "$prs"
fi

# Codex task activity is checked by the parent through list_threads and read_thread when available.
# This shell audit never reads private task transcripts.
now=$(date +%s)

printf "SIZE\tAGE\tMERGED\tDIRTY\tREMOTE\tPR\tPR_CHECK\tBUCKET\tWORKTREE\n"

git worktree list --porcelain | awk '/^worktree /{print $2}' | while read -r wt; do
	[ "$wt" = "$main_wt" ] && continue

	size=$(du -sh "$wt" 2>/dev/null | awk '{print $1}')
	head=$(git -C "$wt" rev-parse HEAD 2>/dev/null)
	head_ts=$(git -C "$wt" log -1 --format='%ct' HEAD 2>/dev/null || echo 0)
	age=$([ "$head_ts" -gt 0 ] 2>/dev/null && echo "$(( (now - head_ts) / 86400 ))d" || echo "?")

	# Squash-merged branches are not ancestors of main, so PR state is the
	# real signal; merge-base only catches fast-forward/rebase merges.
	git merge-base --is-ancestor "$head" origin/main 2>/dev/null && merged=YES || merged=no

	# Report tracked and untracked changes separately; both are user-owned work.
	porcelain=$(git -C "$wt" status --porcelain 2>/dev/null)
	if [ -z "$porcelain" ]; then dirty=clean
	elif printf '%s\n' "$porcelain" | grep -qv '^??'; then
		dirty="wip:$(printf '%s\n' "$porcelain" | grep -cv '^??')"
	else dirty="scratch:$(printf '%s\n' "$porcelain" | grep -c '^??')"; fi

	branch=$(git -C "$wt" symbolic-ref --quiet --short HEAD 2>/dev/null || echo "")
	if [ -z "$branch" ]; then remote=detached
	elif git -C "$wt" show-ref --verify --quiet "refs/remotes/origin/$branch"; then
		[ "$(git -C "$wt" rev-parse "origin/$branch" 2>/dev/null)" = "$head" ] \
			&& remote=pushed \
			|| remote="ahead$(git -C "$wt" rev-list --count "origin/$branch..HEAD" 2>/dev/null)"
	else remote=no-remote; fi

	if [ "$pr_check" = verified ]; then
		pr=$([ -n "$branch" ] && jq -r --arg b "$branch" \
			'.[] | select(.headRefName==$b) | "#\(.number)/\(.state)"' "$prs" | head -1)
		[ -z "$pr" ] && pr="-"
	else
		pr=unknown
	fi

	# The parent cross-checks task activity through native Codex task history.

	case "$dirty" in wip:*) bucket=hold-wip ;; *)
		case "$pr" in *OPEN*) bucket=hold-open-pr ;; *)
			if [ "$pr_check" != verified ]; then bucket=review-unverified-pr
			elif [ "$merged" = YES ] || [ "$pr" != "-" ]; then bucket=safe
			else bucket=review; fi ;;
		esac ;;
	esac

	printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
		"$size" "$age" "$merged" "$dirty" "$remote" "$pr" "$pr_check" "$bucket" "$wt"
done | sort -t$'\t' -k1,1 -rh

rm -f "$prs"
