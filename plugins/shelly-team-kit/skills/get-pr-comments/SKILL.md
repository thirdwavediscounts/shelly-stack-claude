---
name: get-pr-comments
description: Fetch and summarize review comments from the active pull request
---

Read the [runtime contract](../../references/runtime.md) before using this skill.

# Get PR comments

## Trigger

Need a concise, actionable summary of feedback on the active pull request.

## Workflow

Resolve the active PR for the current branch, then summarize both its review comments and discussion comments.

## Output

- Grouped feedback summary
- Action list ordered by priority
- Open questions that still need clarification
