# Local tickets

## What this source contains

The repo's untracked `tickets/` folder at the main checkout root. Resolve it with `git rev-parse --path-format=absolute --git-common-dir`; its parent is the main checkout, even from a worktree.

- `tickets/index.tsv`. One row per ticket: id, title, status, parent, app, branch, pr, updated.
- `tickets/DEV-n/DEV-n.md`. Frontmatter (status, app, type, labels, branch, pr, dates), then the problem or evidence, the planned steps, acceptance checks, links, and a `## Log` of dated comments.
- `tickets/DEV-n/DEV-n-<m>.md`. Sub-tickets. The parent usually carries the "why".
- `tickets/DEV-n/*.tsv`. One row per status change, field change, or decision, with a why and evidence column.
- Attachments such as screenshots, in the same folder.

Tickets are where the product or business context lives: the "we're doing this because the returns queue overcounts" layer.

## How to search it

Read the files with `Read`, `Grep`, and `Glob`, or run the **ticket** skill's `scripts/tickets.py show DEV-n`. Do not query a tracker MCP; Linear is retired.

1. **Start with linked tickets.** If the seed commits, branches, or PRs name a ticket id (`DEV-182`), read that ticket, its `.tsv`, and its Log first.
2. **Match by branch and PR.** Grep `index.tsv` for the seed branch names and PR numbers.
3. **Search by keyword.** Grep `tickets/` for the feature name, key symbol, table name, or error string. Try several phrasings.
4. **Walk the tree.** From a sub-ticket, read the parent. From a parent, list its sub-tickets.
5. **Read the decision rows.** The `.tsv` `why` column often states the reason in one line, with evidence beside it.

## What good evidence looks like here

- A Problem or Evidence section that states the business problem with a source.
- A Log entry or `.tsv` row recording a decision and its reason.
- A parent ticket titled like an initiative.
- A status move to Canceled or Need Human with the reason in `why`.

## Common pitfalls

- **Scope drift.** Acceptance checks may have been rewritten after the build. Read the Log for the scope-change comment.
- **Stale tickets.** Check `updated` and the `.tsv` timestamps against the code's ship date.
- **No folder.** A repo without `tickets/`, or a machine that never had it, is a gap. Report it as "no local tickets", not as "no motivation".

## What to return

For each relevant ticket:
- Ticket id, title, status
- The problem or motivation quoted verbatim from the body, Log, or a `.tsv` `why` cell
- Parent ticket, app, branch, PR
- The file path and line, so the synthesizer can cite it
