#!/usr/bin/env bash
# Read-only worktree prune audit. Classifies every git worktree by size, merge
# state, uncommitted work, remote/PR state, and the most recent chat that
# operated in it. Emits a table sorted by size with a suggested bucket. Never
# deletes anything; deletion stays a human-gated step in the playbook.
#
# Usage: worktree-audit.sh [repo-path]   (defaults to the current repo)
set -u

repo="${1:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -z "$repo" ] && { echo "not in a git repo; pass a repo path" >&2; exit 1; }
cd "$repo" || exit 1

# Main worktree is the first entry; everything else is a candidate.
main_wt=$(git worktree list --porcelain | sed -n 's/^worktree //p' | head -1)

# origin/main drives the merge check. Best-effort; stale is fine for a first pass.
git fetch origin main --quiet 2>/dev/null || echo "warn: could not fetch origin/main; merged column may be stale" >&2

prs=$(mktemp)
pr_lookup=available
command -v jq >/dev/null && gh pr list --author "@me" --state all --limit 1000 \
	--json number,state,headRefName 2>/dev/null > "$prs" || pr_lookup=unavailable

slugify() { printf '%s' "$1" | sed 's/[^A-Za-z0-9-]/-/g'; }
transcripts="$HOME/.claude/projects/$(slugify "$main_wt")"

if command -v rg >/dev/null; then
	search() { rg -o --no-heading --with-filename --no-line-number --hidden --no-ignore -g '*.jsonl' -e "$1" "$transcripts"; }
else
	search() { grep -roE --include='*.jsonl' -e "$1" "$transcripts"; }
fi
NAME='[^/"[:space:]\\]+'
index_transcripts_naming_worktrees() {
	git worktree list --porcelain | sed -n 's/^worktree //p' | grep -vxF "$main_wt" \
		| while IFS= read -r wt; do dirname "$wt"; done | sort -u \
		| while IFS= read -r parent; do
			search "$(printf '%s' "$parent" | sed 's/[][\.*^$+?(){}|]/\\&/g')/$NAME[/\"]"
		done \
		| awk '{ i = index($0, ":"); print substr($0, i + 1, length($0) - i - 1) "\t" substr($0, 1, i - 1) }' \
		| sort -u
}
worktree_transcript_pairs=$(mktemp)
[ -d "$transcripts" ] && index_transcripts_naming_worktrees > "$worktree_transcript_pairs"
main_transcripts_naming_exact_path() {
	case "$(basename "$1")" in
		*[[:space:]\"\\]*) [ -d "$transcripts" ] && grep -rlF -e "$1/" -e "$1\"" "$transcripts" ;;
		*) awk -F'\t' -v w="$1" '$1 == w { print $2 }' "$worktree_transcript_pairs" ;;
	esac
}
transcripts_started_in() {
	find "$HOME/.claude/projects/$(slugify "$1")" -name '*.jsonl' 2>/dev/null
}
now=$(date +%s)

printf "SIZE\tAGE\tMERGED\tDIRTY\tREMOTE\tPR\tLAST_CHAT\tBUCKET\tWORKTREE\n"

git worktree list --porcelain | sed -n 's/^worktree //p' | while IFS= read -r wt; do
	[ "$wt" = "$main_wt" ] && continue

	size=$(du -sh "$wt" 2>/dev/null | awk '{print $1}')
	head=$(git -C "$wt" rev-parse HEAD 2>/dev/null)
	head_ts=$(git -C "$wt" log -1 --format='%ct' HEAD 2>/dev/null || echo 0)
	age=$([ "$head_ts" -gt 0 ] 2>/dev/null && echo "$(( (now - head_ts) / 86400 ))d" || echo "?")

	# Squash-merged branches are not ancestors of main, so PR state is the
	# real signal; merge-base only catches fast-forward/rebase merges.
	git merge-base --is-ancestor "$head" origin/main 2>/dev/null && merged=YES || merged=no

	# Distinguish real WIP (tracked edits) from disposable untracked scratch.
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

	if [ "$pr_lookup" = unavailable ]; then pr="?"
	else
		pr=$([ -n "$branch" ] && jq -r --arg b "$branch" \
			'.[] | select(.headRefName==$b) | "#\(.number)/\(.state)"' "$prs" 2>/dev/null | head -1)
		[ -z "$pr" ] && pr="-"
	fi

	last="-"; last_ts=0
	f=$({ main_transcripts_naming_exact_path "$wt"; transcripts_started_in "$wt"; } \
		| tr '\n' '\0' | xargs -0 stat -f '%m %N' 2>/dev/null | sort -rn | head -1)
	if [ -n "$f" ]; then last_ts=$(echo "$f" | awk '{print $1}')
		last=$(date -r "$last_ts" '+%Y-%m-%d' 2>/dev/null); fi
	recent=$([ "$last_ts" -gt 0 ] 2>/dev/null && [ $(( (now - last_ts) / 86400 )) -le 4 ] && echo yes || echo no)

	case "$dirty" in wip:*) bucket=hold-wip ;; *)
		case "$pr" in *OPEN*) bucket=hold-open-pr ;; *)
			if [ "$recent" = yes ]; then bucket=verify-recent-chat
			elif [ "$pr" = "?" ]; then bucket=unknown
			elif [ "$merged" = YES ] || [ "$pr" != "-" ]; then bucket=safe
			else bucket=review; fi ;;
		esac ;;
	esac

	printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
		"$size" "$age" "$merged" "$dirty" "$remote" "$pr" "$last" "$bucket" "$wt"
done | sort -t$'\t' -k1,1 -rh

rm -f "$prs" "$worktree_transcript_pairs"
