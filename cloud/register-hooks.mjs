// Registers the kit's hooks in ~/.claude/settings.json, keeping whatever is already there.
import { existsSync, readFileSync, writeFileSync } from "node:fs";

const path = `${process.env.HOME}/.claude/settings.json`;
const settings = existsSync(path) ? JSON.parse(readFileSync(path, "utf8")) : {};

const SUPABASE_WRITES =
  "mcp__.*__(execute_sql|apply_migration|deploy_edge_function|create_branch|merge_branch|rebase_branch|reset_branch|delete_branch|pause_project|restore_project)";

const hooks = [
  { event: "SessionStart", command: "bash ~/.claude/hooks/tailscale-up.sh" },
  { event: "SessionStart", command: "bash ~/.claude/hooks/git-staleness-check.sh" },
  { event: "SessionStart", command: "node ~/.claude/hooks/infisical-env.mjs" },
  { event: "SessionStart", command: "bash ~/.claude/hooks/db-tunnel.sh" },
  {
    event: "PreToolUse",
    matcher: SUPABASE_WRITES,
    command:
      "command -v node >/dev/null || { echo 'prod-db-guard: node is not on PATH, blocking the prod call' >&2; exit 2; }; node \"$HOME/.claude/hooks/prod-db-guard.mjs\" || { echo 'prod-db-guard: the guard failed, blocking the prod call' >&2; exit 2; }",
  },
];

settings.hooks ??= {};
for (const { event, matcher, command } of hooks) {
  const script = `.claude/hooks/${command.match(/hooks\/([\w.-]+)/)[1]}`;
  const stale = (h) => h.command !== command && h.command?.includes(script);
  const groups = (settings.hooks[event] ?? []).flatMap((g) => {
    if (!g.hooks?.some(stale)) return [g];
    const kept = g.hooks.filter((h) => !stale(h));
    return kept.length ? [{ ...g, hooks: kept }] : [];
  });
  settings.hooks[event] = groups;
  if (groups.some((g) => g.hooks?.some((h) => h.command === command))) continue;
  groups.push({ ...(matcher && { matcher }), hooks: [{ type: "command", command }] });
}

writeFileSync(path, JSON.stringify(settings, null, 2) + "\n");
