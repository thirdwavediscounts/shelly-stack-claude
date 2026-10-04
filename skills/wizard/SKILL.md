---
name: wizard
description: >-
  Generate an interactive bash script that walks a human through steps only they can do, captures
  each value without the agent seeing it, and writes it to env files, GitHub secrets, or Vercel env
  vars. Use when setup needs a third-party dashboard (eBay developer keys, OAuth apps, Supabase or
  Vercel secrets), a credential only the human can create, or a one-off cutover with manual steps.
  Not for steps the agent can do itself.
argument-hint: "[the setup or cutover to script]"
---

# Wizard

Write a bash script that a human runs to finish a manual procedure. Each stage opens the right page, says exactly what to click and copy, reads the value with hidden input when it is secret, writes it where it belongs, and shows how many stages are left. The agent never sees a secret value, so this is the shape for any credential hand-off with more than one step.

The library in [`scripts/template.sh`](scripts/template.sh) handles the UX: progress, confirmation gates, hidden input, idempotent env upserts, `gh secret`/`gh variable` writes, `vercel env add` through stdin, and a closing summary. Adapted from Matt Pocock's `wizard` skill (MIT, see `LICENSE.mattpocock-skills`).

## Steps

1. **Scope the procedure.** Read the repository before asking. For setup, read `.env.example` files, framework config, `vercel.json`, and `.github/workflows/*` (each `secrets.*` or `vars.*` reference is a value to produce). For a cutover, read the current state, the target state, and the irreversible actions between them. Show the user the ordered stages and the values each produces, and let them add, drop, or reorder. Done when each value has a source page, a destination (env file, GitHub secret, Vercel env var, or none), and a secret or public label.
2. **Map each stage.** Write the exact path a human follows, for example "developer.ebay.com/my/keys, Production keyset, copy the Cert ID". When you do not know the current UI, check the vendor's docs or ask. Never invent a step. Done when a stranger could follow every stage.
3. **Author the script.** Copy `scripts/template.sh` from this skill's directory to `scripts/wizards/<name>.sh` in the target repository, or to a scratch path for a one-time run. Replace the example stage with one `stage` per step in dependency order and set `TOTAL_STAGES`. Use `open_url` before asking for a value from that page, `ask_secret` for every secret, `write_env` for every value the app reads locally, `set_secret` only for values CI reads, `set_vercel_env` for deployed apps, and `confirm` before any irreversible action. Set `ENV_FILE` to the file the app actually loads (`apps/<app>/.env.local`, for example). Add each new key to the matching `.env.example` with a placeholder. Leave the library above the `STAGES` marker unchanged.
4. **Check it statically.** Run `bash -n <script>` and `shellcheck <script>` when installed, then `chmod +x`. Do not run it yourself, since it opens a browser and waits for a human. Trace instead: every value from step 1 is captured and lands where step 1 said, every `set_secret` name matches a `secrets.*` reference in CI, and every `set_vercel_env` name matches the variable the app reads.
5. **Hand off.** Tell the user the command to run and ask for "done" back. Then verify the result yourself without reading the values. Check that the keys exist in the env file with `sed 's/=.*/=<redacted>/'`, list Vercel env names, or run the app's health check.

Commit the script only when the procedure will repeat. A one-time cutover wizard stays out of the repository.

## Reply

- The script path and the exact command to run.
- The stages in order, one line each, with where each value lands.
- Anything the script cannot do and the human must still do by hand.
- After "done", the check you ran and its redacted output.
