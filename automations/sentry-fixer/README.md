# sentry-fixer

Two Claude Code cloud routines that turn Sentry issues into Linear tickets, fix them, and close the loop.

- `sync.md`: hourly, Sonnet 5. New unresolved Sentry issues become Linear `Bug` tickets in Triage. Linear tickets that reached Done get their Sentry issue resolved.
- `autofix.md`: hourly, Opus 4.8. Picks one Triage ticket, fixes it on a `sean/autofix/*` branch, opens a PR, moves the ticket to In Review. Linear's GitHub integration moves it to Done on merge, and the next sync run resolves it on Sentry.

Both use the claude.ai Sentry and Linear connectors. Slack goes through `bin/ticket-slack.mjs` (one `twd-agents` Slack app, per-step username and cat avatar, one thread per ticket found by scanning channel history). It needs `SLACK_TICKET_BOT_TOKEN` and `SLACK_TICKET_CHANNEL` in the cloud environment and is a silent no-op without them; `bin/slack-app-manifest.json` is the app definition. Both routines list `thirdwavediscounts/shelly-stack` as a source so the helper is on disk at `/home/user/shelly-stack`. Neither can reach the Argus Engine VPS, so argus-engine fixes stop at the PR and the ticket says so.

The files here are routine sources, not slash skills. Create or update the routines with `/schedule` and paste the prompt from the matching file. Dedupe key is the Sentry short ID in the ticket title, plus a `<!-- sentry:<issue id> -->` marker in the description.
