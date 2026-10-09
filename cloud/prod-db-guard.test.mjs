import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

const KIT = fileURLToPath(new URL(".", import.meta.url));
const GUARD = join(KIT, "hooks", "prod-db-guard.mjs");
const PROD = "mcp__supabase-production__";
const home = mkdtempSync(join(tmpdir(), "prod-db-guard-"));

function run(stdin, script = GUARD) {
  const r = spawnSync("node", [script], { input: stdin, env: { ...process.env, HOME: home }, encoding: "utf8" });
  return { status: r.status, out: r.stdout ? JSON.parse(r.stdout).hookSpecificOutput : null };
}

const sql = (query, extra = {}) => JSON.stringify({ tool_name: `${PROD}execute_sql`, tool_input: { query }, ...extra });
const tool = (name, tool_input = {}) => JSON.stringify({ tool_name: `${PROD}${name}`, tool_input });

const CASES = [
  ["allow", "plain select", sql("select * from sales where id = 1")],
  ["allow", "select with an aggregate", sql("select count(*) from sales")],
  ["allow", "select with a schema-qualified read-only builtin", sql("select pg_catalog.now()")],
  ["allow", "insert", sql("insert into notes (body) values ('x')")],
  ["allow", "create table", sql("create table t (id int)")],
  ["allow", "insert whose string mentions a function call", sql("insert into notes (body) values ('select cron.unschedule(1)')")],
  ["allow", "explicit 10s timeout", sql("set local statement_timeout = '10s'; select 1")],
  ["ask", "select calling cron.unschedule", sql("select cron.unschedule('nightly')")],
  ["ask", "select calling an rpc", sql("select rpc_sale_link_manual(1,2)")],
  ["ask", "select calling a quoted-schema rpc", sql('select "public".rpc_sale_link_manual(1,2)')],
  ["ask", "select distinct calling a function", sql("select distinct pg_terminate_backend(pid) from pg_stat_activity")],
  ["ask", "session_replication_role", sql("set session_replication_role = replica; insert into t values (1)")],
  ["ask", "set local session_replication_role", sql("set local session_replication_role to replica")],
  ["ask", "delete with where", sql("delete from sales where id = 1")],
  ["ask", "update without where", sql("update sales set price = 0")],
  ["ask", "drop table", sql("drop table sales")],
  ["ask", "truncate", sql("truncate sales")],
  ["ask", "do block", sql("do $$ begin perform 1; end $$")],
  ["ask", "upsert", sql("insert into t values (1) on conflict (id) do update set v = 2")],
  ["ask", "grant to anon", sql("grant select on t to anon")],
  ["ask", "unknown statement", sql("vacuum sales")],
  ["ask", "migration with a drop", tool("apply_migration", { query: "alter table t drop column c" })],
  ["ask", "edge function deploy", tool("deploy_edge_function", { name: "f" })],
  ["ask", "unparseable input", "not json"],
  ["ask", "null input", "null"],
  ["ask", "array input", "[]"],
  ...[
    "select pid, pg_terminate_backend(pid) from pg_stat_activity",
    "select coalesce(rpc_sale_link_manual(1,2),0)",
    "select * from cron.unschedule('nightly')",
    "select (cron.unschedule(1))",
    "select all cron.unschedule(1)",
    "with x as (select cron.unschedule(1)) select * from x",
    "select count(*) from t where pg_terminate_backend(1)",
    'set "session_replication_role" = replica',
    "insert into t select cron.unschedule(1)",
    "insert into t values (pg_terminate_backend(1))",
  ].map((q) => ["ask", q, sql(q)]),
  ...[
    "select distinct on (sku) sku, price from listings order by sku, created_at desc",
    "select cast(price as numeric(10,2)) from sales",
    "select exists(select 1 from sales where id = 1)",
    "select extract(epoch from now() - created_at) from sales",
    "select round(avg(price), 2) from sales",
    "select json_build_object('id', id, 'n', count(*) over (partition by sku)) from sales",
    "select pg_size_pretty(pg_total_relation_size('sales'))",
    "select sku from sales where id in (1, 2) and price::numeric(10,2) > 0",
    "insert into t (id, at) values (1, now()) on conflict (id) do nothing",
  ].map((q) => ["allow", q, sql(q)]),
  ["deny", "delete_branch", tool("delete_branch", { branch_id: "b" })],
  ["deny", "reset_branch", tool("reset_branch", { branch_id: "b" })],
  ["deny", "timeout above 30s", sql("set statement_timeout = '5min'; select 1")],
  ["deny", "timeout reset", sql("reset statement_timeout; select 1")],
  ["deny", "ask in auto mode", sql("delete from sales where id = 1", { permission_mode: "auto" })],
  ["pass", "staging server", JSON.stringify({ tool_name: "mcp__supabase-staging__execute_sql", tool_input: { query: "drop table t" } })],
  ["pass", "another project", tool("execute_sql", { query: "drop table t", project_id: "other" })],
  ["pass", "read-only tool", tool("list_tables")],
];

for (const [want, name, stdin] of CASES) {
  test(`${want}: ${name}`, () => {
    const { status, out } = run(stdin);
    assert.equal(status, 0);
    assert.equal(out?.permissionDecision ?? "pass", want, out?.permissionDecisionReason);
  });
}

test("allowed ad-hoc SQL gets the 30s timeout prefix", () => {
  const { out } = run(sql("select 1"));
  assert.match(out.updatedInput.query, /^SET LOCAL statement_timeout = '30s';\nselect 1$/);
});

test("install replaces the old guard entry, and the registered command blocks on failure", () => {
  const h = join(home, "install");
  mkdirSync(join(h, ".claude"), { recursive: true });
  const old = `command -v node >/dev/null || { echo 'prod-db-guard: node is not on PATH, blocking the prod call' >&2; exit 2; }; node "$HOME/.claude/hooks/prod-db-guard.mjs"`;
  const mine = { matcher: "mine", hooks: [{ type: "command", command: "echo keep-me" }] };
  writeFileSync(
    join(h, ".claude", "settings.json"),
    JSON.stringify({ hooks: { PreToolUse: [mine, { matcher: "x", hooks: [{ type: "command", command: old }] }] } }),
  );
  const env = { ...process.env, HOME: h };
  execFileSync("bash", [join(KIT, "install.sh")], { env });
  execFileSync("bash", [join(KIT, "install.sh")], { env });

  const pre = JSON.parse(readFileSync(join(h, ".claude", "settings.json"), "utf8")).hooks.PreToolUse;
  const guards = pre.flatMap((g) => g.hooks).filter((x) => x.command.includes("prod-db-guard.mjs"));
  assert.equal(guards.length, 1);
  assert.notEqual(guards[0].command, old);
  assert.deepEqual(pre[0], mine);

  const shell = (input) => spawnSync("bash", ["-c", guards[0].command], { input, env, encoding: "utf8" });
  assert.equal(JSON.parse(shell("null").stdout).hookSpecificOutput.permissionDecision, "ask");
  writeFileSync(join(h, ".claude", "hooks", "prod-db-guard.mjs"), "process.exit(1);\n");
  assert.equal(shell(sql("select 1")).status, 2);
  rmSync(join(h, ".claude", "hooks", "prod-db-guard.mjs"));
  assert.equal(shell(sql("select 1")).status, 2);
  const noNode = spawnSync("/bin/bash", ["-c", guards[0].command], { input: "{}", env: { HOME: h, PATH: "/nonexistent" } });
  assert.equal(noNode.status, 2);
});

test("register-hooks drops the old guard command from a group it shares with another hook", () => {
  const h = join(home, "mixed");
  mkdirSync(join(h, ".claude"), { recursive: true });
  const old = `node "$HOME/.claude/hooks/prod-db-guard.mjs"`;
  const keep = { type: "command", command: "echo keep-me" };
  writeFileSync(
    join(h, ".claude", "settings.json"),
    JSON.stringify({ hooks: { PreToolUse: [{ matcher: "x", hooks: [{ type: "command", command: old }, keep] }] } }),
  );
  execFileSync("node", [join(KIT, "register-hooks.mjs")], { env: { ...process.env, HOME: h } });

  const commands = JSON.parse(readFileSync(join(h, ".claude", "settings.json"), "utf8"))
    .hooks.PreToolUse.flatMap((g) => g.hooks)
    .map((x) => x.command);
  assert.ok(!commands.includes(old));
  assert.ok(commands.includes(keep.command));
  assert.equal(commands.filter((c) => c.includes("prod-db-guard.mjs")).length, 1);
});

test.after(() => rmSync(home, { recursive: true, force: true }));
