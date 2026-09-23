---
name: get-pr-comments
description: Fetch review and discussion comments from the current branch's pull request and summarize them as a prioritized action list. Use when asked what reviewers said, what is outstanding on a PR, or to address review feedback.
disable-model-invocation: true
---

Read the [runtime contract](../../references/runtime.md) before using this skill.

# Get PR comments

## Workflow

Resolve the active PR for the current branch, then summarize both its review comments and discussion comments.

## Output

- Grouped feedback summary
- Action list ordered by priority
- Open questions that still need clarification
