---
name: no-comments
description: Spawn a native read-only Comment Sicko reviewer, fix accepted findings, and offer structural encodings for claimed constraints. Use for 'strip the comments', 'is this PR clean of comments', 'run comment sicko', or before handing a diff to review.
---

# No comments

Spawn Comment Sicko as a native read-only subagent. Act only on findings verified against the scoped code.

## Scope

Use the caller's files or diff. Otherwise use the current diff against the base branch, default `main`, including the working tree.

## Steps

1. Read `references/comment-sicko.md`. Dispatch one reviewer with that prompt, the scope, and the configured `code review` model and reasoning effort through the native runtime contract's read-only worker branch.
2. Inspect its report and any diff. Reject application-code edits, scope escapes, exception-protected deletions, misstated `MUST KILL` reasons, and flags that treat intentional code as guilty. Audit missed scoped lint and TypeScript suppressions. Before accepting thin `IMPORTANT` or `do not remove` kills or keeps, use `/how` or `/why` on the named symbol. Rerun one rejected report with the failure named. Reject a second failure, report it open, and fail `/no-comments`.
3. Fix trivial accepted flags directly by deleting a dead path, dropping a parameter, or using the real API. If a fix needs a shape, run `/architect` once for the accepted set and surrounding code. Stop at the sketch before implementation.
4. Implement the smallest root-cause fix in scope. Remove every named workaround. If the root cause is out of scope, land the smallest in-scope fix and report the remainder.
5. For comments claiming an external constraint, offer the cheapest in-scope type, runtime check, test, or CI lint. Wait for approval before encoding it unless the caller already authorized unattended changes. Keep only constraints proven to come from something the project cannot change.
6. Report deletion count, restored comments, reruns, architect sketch, fixes, encoding offers, completed encodings, unenforced constraints, and open work.
