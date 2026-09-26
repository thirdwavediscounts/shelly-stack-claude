#!/usr/bin/env bash
# Installs shelly-stack's cloud kit into ~/.claude on a Claude Code cloud VM: the prod
# Supabase guard, the stale-checkout warning, the tailnet join for `ssh twd`,
# the app env files from Infisical dev, and the Postgres tunnel over `ssh twd`.
# Cloud sessions don't carry over local ~/.claude, so the environment's setup script runs this.
set -eu
KIT=$(cd "$(dirname "$0")" && pwd)
mkdir -p ~/.claude/hooks
cp "$KIT"/hooks/* ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.sh
node "$KIT/register-hooks.mjs"
echo "cloud-kit: hooks installed"
