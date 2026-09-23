# sentry-fixer

Two Claude Code cloud routines that turn Sentry issues into Linear tickets, fix them, and close the loop.

- `sync.md`: hourly, Fable 5.1. New unresolved Sentry issues become Linear `Bug` tickets in Triage. Linear tickets that reached Done get their Sentry issue resolved.
- `autofix.md`: hourly, Fable 5.1 in shelly mode with plugin subagents. Picks one Triage ticket, fixes it on a `sean/autofix/*` branch, opens a PR, moves the ticket to In Review. Linear's GitHub integration moves it to Done on merge, and the next sync run resolves it on Sentry.

Both use the claude.ai Sentry and Linear connectors. Slack goes through `bin/ticket-slack.mjs` (one `twd-agents` Slack app, per-step username and cat avatar, one thread per ticket found by scanning channel history). It needs `SLACK_TICKET_BOT_TOKEN` and `SLACK_TICKET_CHANNEL` in the cloud environment and is a silent no-op without them; `bin/slack-app-manifest.json` is the app definition. Both routines list `thirdwavediscounts/shelly-stack-claude` as a source so the helper is on disk at `/home/user/shelly-stack-claude`. Neither can reach the Argus Engine VPS, so argus-engine fixes stop at the PR and the ticket says so.

The files here are routine sources, not slash skills. Create or update the routines with `/schedule` and paste the prompt from the matching file. Dedupe key is the Sentry short ID in the ticket title, plus a `<!-- sentry:<issue id> -->` marker in the description.

## Cloud helpers (`cloud/`)

- `shelly-stack-models.md`: the model rule the setup script copies to `~/.claude/rules/` so the lead delegates to the plugin's pinned agents.
- `materialize.sh`: writes the verify-live creds and the Infisical `.env` exports from the environment's variables (`VERIFY_LIVE_CREDS`, `INFISICAL_PROJECT_ID`, `INFISICAL_CLIENT_ID`, `INFISICAL_CLIENT_SECRET`). No-op when they are unset.
- `verify-live.sh <TICKET> <app> <feature>`: starts the app's isolated dev server on the current branch, drives one feature as the verify account through `scripts/verification/control.mjs` with recording on, posts the webm to the ticket's thread as `verify-live`, stops the server. Sets `AGENT_BROWSER_ARGS` to `--no-sandbox,--ssl-version-max=tls1.2` behind the cloud proxy, which rejects Chromium's TLS 1.3, and installs `ffmpeg` if the image lacks it. Add `apt-get install -y --no-install-recommends ffmpeg` to the environment setup script to skip that install per run.
