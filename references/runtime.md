# Claude Code runtime

Use the active tool catalog and repository instructions. This package provides workflows, not browser binaries, credentials, or service integrations.

## Skills and tools

Invoke companion skills as `/shelly-stack:<name>`. Resolve files relative to the installed skill path, never from a guessed checkout or cache directory. Reuse the project's verification skill and available browser or terminal tools. Read the selected tool's skill before driving it. If no suitable tool is available, report the exact unverified step.

## Authorization

An explicit `review-and-ship` or `new-branch-and-pr` request includes focused commits, pushes, and opening or updating the PR. A review, test run, or local fix alone does not. CI repair may push when the current request authorizes bringing the PR to green. Honor existing authorization without asking again. Merge, deploy, send messages, or rewrite published history only when separately authorized. Never bypass required checks. Preserve unrelated changes and follow the repository's branch, commit, and PR conventions.

## Reviewers

Do the work in the parent unless the user or active instructions permit delegation. When an independent reviewer is required, use an available contained read-only agent. If the runtime cannot enforce that boundary, report independent review unavailable. A prompt asking a writable agent not to edit is not enforced isolation. Collect any external evidence in the parent through authorized read-only tools and supply the relevant excerpts to the reviewer. Do not send reviewer output directly to an external service.

The [CI watcher](ci-watcher.md) supplies a bounded status report. The [maintainability reviewer](maintainability-reviewer.md) supplies findings without edits. These prompts also work in the parent when independence is not required. Never recursively invoke the parent workflow from a reviewer.

## CI and waits

Inspect all PR-attached checks with `gh pr checks`. Use GitHub Actions job logs only for checks actually hosted there. Resolve the PR head before and after a check pass. A stale result or an empty check set does not establish success. Missing required checks remain unverified.

Current-turn polling uses bounded commands and waits no longer than 60 seconds. Stay in the current turn until the requested terminal state or a real blocker. A future recurring check requires an explicit request and an available scheduling tool. Notify only on meaningful changes, completion, failure, or required user action. Never invent a background monitor.

## History

Use the current conversation first. For requested earlier history, read only the active workspace's `~/.claude/projects/<slug>/` directory, where the absolute workspace path has each slash replaced with a hyphen. Never scan unrelated projects. If the workspace cannot be resolved, use a user-provided transcript or a narrow digest. Draft status updates locally unless the user asks to send them.
