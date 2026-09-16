# Codex runtime

Use the active tool catalog and repository instructions. This package provides workflows, not browser binaries, credentials, or service integrations.

## Skills and tools

Invoke companion skills as `$shelly-team-kit:<name>`. Resolve support files from the absolute skill path in the active catalog. Reuse the project's verification skill and exposed browser or terminal tools. Read the selected tool's skill before driving it. Do not assume an in-app browser, a particular connector, or a screenshot tool exists. Report the exact unverified step when a required capability is absent.

## Authorization

An explicit `review-and-ship` or `new-branch-and-pr` request includes focused commits, pushes, and opening or updating the PR. A review, test run, or local fix alone does not. CI repair may push when the current request authorizes bringing the PR to green. Honor existing authorization without asking again. Merge, deploy, send messages, or rewrite published history only when separately authorized. Never bypass required checks. Preserve unrelated changes and follow repository naming conventions.

## Reviewers

Do the work in the parent unless the user or active instructions permit delegation. If Shelly Stack is installed, read its native runtime contract for model-role selection and the enforced read-only worker branch. Otherwise use an exposed spawn capability only when it accepts an enforced read-only sandbox. If neither is available, report independent review unavailable. Never call a writable child read-only based on its prompt.

Use `list_agents`, `spawn_agent`, and `wait_agent` only when exposed. Bound fan-out by the actual available capacity. Consume the separately delivered final result after waiting. Do not create a separate user task to substitute for a subagent. Pass no model override unless the user or applicable instructions provide it.

The [CI watcher](ci-watcher.md) supplies a bounded status report. The [maintainability reviewer](maintainability-reviewer.md) supplies findings without edits. These prompts also work in the parent when independence is not required. Collect required external evidence in the parent and pass only relevant excerpts. Never recursively invoke the parent workflow from a reviewer.

## CI and waits

Inspect all PR-attached checks with `gh pr checks`. Use GitHub Actions job logs only for checks actually hosted there. Resolve the PR head before and after a check pass. A stale result or an empty check set does not establish success. Missing required checks remain unverified.

Current-turn polling uses bounded commands and waits no longer than 60 seconds. Stay in the current turn until the requested terminal state or a real blocker. A future recurring check requires an explicit request and an exposed automation provider. Notify only on meaningful changes, completion, failure, or required user action. Do not create a persistent goal or automation for an ordinary plan or current-turn CI wait.

## History

Use the current conversation first. For requested earlier history, use exposed task history tools scoped to the active workspace and date window. If those tools are unavailable, use a user-provided exact transcript path or a narrow digest. Never scan unrelated session records. Draft status updates locally unless the user asks to send them.
