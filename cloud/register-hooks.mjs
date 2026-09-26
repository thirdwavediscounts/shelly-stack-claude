// Registers the kit's hooks in ~/.claude/settings.json, keeping whatever is already there.
// Idempotent: a hook whose command is already registered is skipped.
import { existsSync, readFileSync, writeFileSync } from "node:fs";

const path = `${process.env.HOME}/.claude/settings.json`;
const settings = existsSync(path) ? JSON.parse(readFileSync(path, "utf8")) : {};

const SUPABASE_WRITES =
  "mcp__.*__(execute_sql|apply_migration|deploy_edge_function|create_branch|merge_branch|rebase_branch|reset_branch|delete_branch|pause_project|restore_project)";

const hooks = [
  { event: "SessionStart", command: "bash ~/.claude/hooks/tailscale-up.sh" },
  { event: "SessionStart", command: "bash ~/.claude/hooks/git-staleness-check.sh" },
  {
    event: "PreToolUse",
    matcher: SUPABASE_WRITES,
    command:
      "command -v node >/dev/null || { echo 'prod-db-guard: node is not on PATH, blocking the prod call' >&2; exit 2; }; node \"$HOME/.claude/hooks/prod-db-guard.mjs\"",
  },
];

settings.hooks ??= {};
for (const { event, matcher, command } of hooks) {
  const groups = (settings.hooks[event] ??= []);
  if (groups.some((g) => g.hooks?.some((h) => h.command === command))) continue;
  groups.push({ ...(matcher && { matcher }), hooks: [{ type: "command", command }] });
}

writeFileSync(path, JSON.stringify(settings, null, 2) + "\n");
