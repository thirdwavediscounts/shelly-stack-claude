#!/usr/bin/env node
// PreToolUse guard for PROD Supabase (project womayabywfxycbvqxatf), cloud edition.
// Cloud sessions reach Supabase through claude.ai connectors whose server names aren't
// `supabase-production`, and one connector is account-scoped (tools take project_id). So the
// matcher (cloud/register-hooks.mjs) sends every server's mutating Supabase tools here, and
// the prod check below decides whether the call targets prod.
//
// Policy for calls that target prod:
//   - Read-only tools / plain SELECTs .......... allow (prod diagnosis stays frictionless)
//   - Additive SQL (CREATE, CREATE OR REPLACE, INSERT, COMMENT, GRANT to non-public roles)
//                                              .. allow
//   - Branch delete/reset ...................... DENY outright (cannot be approved by a mis-click)
//   - Catastrophic SQL (DROP TABLE/SCHEMA/..., TRUNCATE, DELETE|UPDATE without WHERE)
//                                              .. ASK with a CATASTROPHIC warning
//   - Destructive SQL (DELETE, UPDATE, upsert DO UPDATE, MERGE, other DROPs, RENAME,
//     column TYPE change, REVOKE, DISABLE RLS/triggers, GRANT to anon/public, DO, CALL,
//     SELECT of a function not on the read-only list, SET session_replication_role)
//                                              .. ASK (forces your explicit approval prompt)
//   - Any statement or tool it can't classify .. ASK
//   - execute_sql .............................. rewritten to run under SET LOCAL
//                                                statement_timeout = '30s'; an explicit
//                                                timeout above 30s is DENIED
//
// Deterministic, so prompt injection cannot talk the model past it. The human approval
// is the real backstop; the SQL parsing below is best-effort (a tokenizer plus per-statement
// regexes, not a full parser), so it errs toward ASK when unsure.

import { appendFileSync, readFileSync } from "node:fs";

// Modes where "ask" never reaches a human: auto mode's classifier decides it. Bypass mode
// still shows the prompt (seen locally), so it isn't listed.
// There the guard denies instead, so prod writes still need a person.
const UNATTENDED_MODES = new Set(["auto", "dontAsk"]);

// Every call leaves a line in ~/.claude/prod-db-guard.log, so a session can prove the
// guard ran and what it decided.
function log(line) {
  try {
    appendFileSync(`${process.env.HOME}/.claude/prod-db-guard.log`, `${new Date().toISOString()} ${line}\n`);
  } catch {}
}

function emit(output) {
  const out = output.hookSpecificOutput;
  const mode = input?.permission_mode ?? "unknown";
  if (out.permissionDecision === "ask" && UNATTENDED_MODES.has(mode)) {
    out.permissionDecision = "deny";
    out.permissionDecisionReason += ` Blocked: '${mode}' mode can't get a human approval. Ask Sean to run it, or switch the session to Accept edits (cloud) or default mode (local) and retry.`;
  }
  log(`${input?.tool_name ?? "?"} mode=${mode} decision=${out.permissionDecision}`);
  process.stdout.write(JSON.stringify(output));
  process.exit(0);
}

function decide(permissionDecision, reason) {
  emit({
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision, // "allow" | "deny" | "ask"
      permissionDecisionReason: reason,
    },
  });
}

let input;
process.on("uncaughtException", (err) => {
  decide("ask", `prod-db-guard: the guard crashed (${err?.message ?? err}). Review the call, then approve to run.`);
});

try {
  input = JSON.parse(readFileSync(0, "utf8"));
} catch {
  // Matcher guarantees this is a prod-server tool; if we can't read it, don't guess — ask.
  decide("ask", "prod-db-guard: could not parse tool input — approve manually after review.");
}

const tool = String(input.tool_name || "");
const shortTool = tool.split("__").pop() || "";
const ti = input.tool_input || {};
const sql = String(ti.query ?? ti.sql ?? "");

// Account-scoped tools name their project; project-scoped servers don't, so those count as
// prod unless the server is a known staging one (fail closed).
const PROD_REF = "womayabywfxycbvqxatf";
const STAGING_SERVERS = new Set(["supabase-staging", "88f19cf8-3c27-4155-b68e-81416b93b810"]);
const server = tool.split("__")[1] || "";
const targetsProd =
  ti.project_id !== undefined
    ? ti.project_id === PROD_REF
    : !STAGING_SERVERS.has(server) && !/staging/i.test(server);
if (!targetsProd) {
  log(`${tool} mode=${input.permission_mode ?? "unknown"} decision=pass (not prod)`);
  process.exit(0);
}

// Prod tools that only ever read — let them through untouched.
const READONLY_TOOLS = new Set([
  "get_project_url",
  "get_publishable_keys",
  "get_advisors",
  "get_edge_function",
  "list_tables",
  "list_extensions",
  "list_migrations",
  "list_edge_functions",
  "list_branches",
  "generate_typescript_types",
  "search_docs",
  "query_logs",
]);
if (READONLY_TOOLS.has(shortTool)) process.exit(0);

// Branch lifecycle ops that would wipe/roll prod — never approvable.
const CATASTROPHIC_TOOLS = new Set(["delete_branch", "reset_branch"]);
if (CATASTROPHIC_TOOLS.has(shortTool)) {
  decide(
    "deny",
    `prod-db-guard: '${shortTool}' on prod is blocked. Do this on staging or via a reviewed runbook.`,
  );
}

// Edge function deploys and branch create/merge/rebase are not SQL this hook can read.
if (shortTool !== "execute_sql" && shortTool !== "apply_migration") {
  decide("ask", `prod-db-guard: '${shortTool}' changes PROD. Review it, then approve to run.`);
}

// Blanks comments, string literals, and quoted identifiers so their contents can't trip or
// hide keywords. Dollar-quoted bodies become BODY in `outer` and stay (recursively
// cleaned) in `full`: a function body doesn't run at CREATE time, but a DO body does.
function clean(text) {
  let full = "";
  let outer = "";
  let i = 0;
  const emit = (s) => {
    full += s;
    outer += s;
  };
  while (i < text.length) {
    const c = text[i];
    const next = text[i + 1];
    if (c === "-" && next === "-") {
      const end = text.indexOf("\n", i);
      i = end === -1 ? text.length : end;
      emit(" ");
    } else if (c === "/" && next === "*") {
      const end = text.indexOf("*/", i + 2);
      i = end === -1 ? text.length : end + 2;
      emit(" ");
    } else if (c === "'") {
      const backslashEscapes = /[eE]$/.test(text.slice(0, i)) && !/\w[eE]$/.test(text.slice(0, i));
      i++;
      while (i < text.length) {
        if (backslashEscapes && text[i] === "\\") i += 2;
        else if (text[i] === "'" && text[i + 1] === "'") i += 2;
        else if (text[i] === "'") break;
        else i++;
      }
      i++;
      emit(" '' ");
    } else if (c === '"') {
      const end = text.indexOf('"', i + 1);
      i = end === -1 ? text.length : end + 1;
      emit(" ident ");
    } else if (c === "$" && /^\$(?:[A-Za-z_]\w*)?\$/.test(text.slice(i))) {
      const tag = text.slice(i).match(/^\$(?:[A-Za-z_]\w*)?\$/)[0];
      const end = text.indexOf(tag, i + tag.length);
      const body = text.slice(i + tag.length, end === -1 ? text.length : end);
      i = end === -1 ? text.length : end + tag.length;
      full += ` ${clean(body).full} `;
      outer += " BODY ";
    } else {
      emit(c);
      i++;
    }
  }
  return { full, outer };
}

const { full, outer } = clean(sql);

// An upsert's DO UPDATE SET only ever touches the conflicting row, so it is not the
// unbounded UPDATE the pattern below hunts for. It is still destructive further down.
const scan = full.replace(/\bDO\s+UPDATE\s+SET\b/gi, "DO UPSERT");

const CATASTROPHIC_SQL = [
  /\bDROP\s+(TABLE|SCHEMA|DATABASE|MATERIALIZED\s+VIEW|VIEW|FUNCTION|INDEX|ROLE|TYPE|SEQUENCE|TRIGGER|POLICY)\b/i,
  /\bTRUNCATE\b/i,
  /\bDELETE\s+FROM\b(?![\s\S]*\bWHERE\b)/i, // DELETE with no WHERE anywhere in the statement
  /\bUPDATE\b[\s\S]*?\bSET\b(?![\s\S]*\bWHERE\b)/i, // UPDATE ... SET with no WHERE
];
const catastrophic = CATASTROPHIC_SQL.some((re) => re.test(scan));

// Each statement is classified by its leading keyword. Anything not matched here asks.
const SAFE_START =
  /^(SELECT|WITH|EXPLAIN|SHOW|TABLE|VALUES|CREATE|INSERT|COMMENT|GRANT|REFRESH|ANALYZE|SET|RESET|BEGIN|START|COMMIT|END|NOTIFY)\b/i;
const READ_START = /^(SELECT|WITH|EXPLAIN|SHOW|TABLE|VALUES|SET)\b/i;
const words = (text) => new Set(text.trim().split(/\s+/));
const READ_ONLY_FUNCTIONS = words(`
  count sum avg min max now coalesce nullif greatest least lower upper length trim substring replace
  split_part concat format md5 to_char date_trunc date_part round floor ceil abs array_agg string_agg
  json_agg jsonb_agg json_build_object jsonb_build_object to_jsonb row_to_json jsonb_array_elements
  jsonb_each jsonb_object_keys array_length cardinality generate_series unnest percentile_cont
  row_number rank dense_rank lag lead first_value bool_and bool_or pg_typeof pg_size_pretty
  pg_total_relation_size pg_relation_size current_setting version
`);
const SQL_KEYWORDS = words(`
  select distinct all from where and or not in exists any some on using as join lateral over filter
  within values row array cast extract position case when then else union intersect except explain
  by having limit offset is like ilike between conflict
  numeric decimal varchar char character timestamp timestamptz time interval bit
`);
const CALL = /(?:([A-Za-z_]\w*)\s*\.\s*)?([A-Za-z_]\w*)\s*\(/g;
const RUNS_CALLS = /^(SELECT|WITH|VALUES|TABLE|EXPLAIN)\b/i;
const INSERT_ROWS = /^INSERT\b[\s\S]*?\b((?:SELECT|VALUES)\b[\s\S]*)/i;
const callSite = (s) => (RUNS_CALLS.test(s) ? s : (INSERT_ROWS.exec(s)?.[1] ?? ""));
const callsWritableFunction = (s) =>
  [...callSite(s).matchAll(CALL)].some(([, schema, name]) => {
    const fn = name.toLowerCase();
    if (!schema) return !READ_ONLY_FUNCTIONS.has(fn) && !SQL_KEYWORDS.has(fn);
    return schema.toLowerCase() !== "pg_catalog" || !READ_ONLY_FUNCTIONS.has(fn);
  });
const DESTRUCTIVE_IN_STATEMENT = [
  /^SET\s+(LOCAL\s+|SESSION\s+)?(session_replication_role|ident)\b/i,
  /^WITH\b[\s\S]*\b(DELETE\s+FROM|UPDATE\s+\S+\s+SET|MERGE\s+INTO|INSERT\b[\s\S]*\bDO\s+UPDATE)\b/i,
  /^INSERT\b[\s\S]*\bDO\s+UPDATE\b/i,
  /^GRANT\b[\s\S]*\bTO\s+([\s\S]*,\s*)?(anon|public)\b/i,
  /^ALTER\b[\s\S]*\bDROP\b(?!\s+NOT\s+NULL)/i,
  /^ALTER\b[\s\S]*\b(RENAME|DISABLE|NO\s+FORCE|SET\s+SCHEMA)\b/i,
  /^ALTER\b[\s\S]*\bALTER\s+(COLUMN\s+)?\S+\s+(SET\s+DATA\s+)?TYPE\b/i,
];
// ALTER is additive unless DESTRUCTIVE_IN_STATEMENT flags it.
const ALTER_START = /^ALTER\b/i;
// ON CONFLICT DO NOTHING/UPDATE is not a DO block; DO BODY or DO LANGUAGE x BODY is.
const DO_BLOCK = /\bDO\s+(LANGUAGE\s+\S+\s+)?(BODY|'')/i;

const statements = outer
  .split(";")
  .map((s) => s.replace(/\s+/g, " ").trim())
  .filter(Boolean);

if (statements.length === 0) {
  decide("ask", `prod-db-guard: '${shortTool}' has no SQL this hook can read. Review it, then approve to run.`);
}

const flagged = statements.filter(
  (s) =>
    DO_BLOCK.test(s) ||
    callsWritableFunction(s) ||
    DESTRUCTIVE_IN_STATEMENT.some((re) => re.test(s)) ||
    !(SAFE_START.test(s) || ALTER_START.test(s)),
);
const isRead = statements.every((s) => READ_START.test(s)) && flagged.length === 0;
const askReason = catastrophic
  ? "prod-db-guard: CATASTROPHIC SQL on PROD (DROP / TRUNCATE / DELETE|UPDATE without WHERE). This can destroy fleet-wide data. Approve only if it was proven on staging and you mean to run it on prod."
  : flagged.length > 0
    ? `prod-db-guard: destructive or unrecognized SQL on PROD: ${flagged
        .map((s) => (s.length > 80 ? `${s.slice(0, 80)}…` : s))
        .join(" | ")}. Review the statement, then approve to run.`
    : null;

// Migrations keep the role's default timeout because index builds legitimately run long.
if (shortTool === "apply_migration") {
  if (askReason) decide("ask", askReason);
  process.exit(0); // additive changes only
}

// Ad-hoc SQL on the 2-core prod primary runs under a short statement_timeout. The MCP
// sends the whole string as one implicit transaction, so SET LOCAL covers every
// statement in it and resets when the call ends.
const TIMEOUT_CAP_MS = 30_000;
const TIMEOUT_PREFIX = "SET LOCAL statement_timeout = '30s';\n";
const TIMEOUT_HELP =
  "Prefix the query with `SET LOCAL statement_timeout = '30s';` (or less), or drop your timeout and the guard adds one. Long investigations belong on supabase-staging.";

// Statements Postgres refuses inside a transaction block, so a SET LOCAL prefix would
// break them. They run untimed, so they always need approval.
const NO_TX_BLOCK = /\b(CONCURRENTLY|VACUUM|ALTER\s+SYSTEM|CREATE\s+DATABASE)\b/i;

const DAY_MS = 86_400_000;
const UNIT_MS = { us: 0.001, ms: 1, s: 1000, min: 60_000, h: 3_600_000, d: DAY_MS };
function timeoutMs(value) {
  const m = /^'?\s*(\d+(?:\.\d+)?)\s*(us|ms|s|min|h|d)?\s*'?$/i.exec(value.trim());
  return m ? Number(m[1]) * UNIT_MS[(m[2] || "ms").toLowerCase()] : NaN;
}

// Timeout values are string literals, which `full` blanks, so read them from the SQL with
// only comments stripped.
const norm = sql.replace(/--[^\n]*/g, " ").replace(/\/\*[\s\S]*?\*\//g, " ");
const SET_TIMEOUT = /\bSET\s+(?:LOCAL\s+|SESSION\s+)?statement_timeout\s*(?:=|\bTO\b)\s*('[^']*'|[^;\s]+)/gi;
const OTHER_TIMEOUT_CHANGE = /\bRESET\s+statement_timeout\b|\bset_config\s*\(\s*'statement_timeout'/i;
const explicit = [...norm.matchAll(SET_TIMEOUT)].map((m) => timeoutMs(m[1]));
if (OTHER_TIMEOUT_CHANGE.test(norm) || explicit.some((ms) => !(ms > 0 && ms <= TIMEOUT_CAP_MS))) {
  decide(
    "deny",
    `prod-db-guard: prod ad-hoc SQL must run with statement_timeout between 1ms and 30s; this query sets it higher, to 0/DEFAULT, or in a form the guard cannot read. ${TIMEOUT_HELP}`,
  );
}

if (explicit.length === 0 && NO_TX_BLOCK.test(norm)) {
  decide(
    "ask",
    `${askReason ?? `prod-db-guard: '${shortTool}' writes PROD. Review the statement, then approve to run.`} It cannot run inside a transaction, so it runs WITHOUT the 30s timeout.`,
  );
}

const updatedInput = explicit.length > 0 ? ti : { ...ti, query: TIMEOUT_PREFIX + sql };
emit({
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: askReason ? "ask" : "allow",
    permissionDecisionReason:
      askReason ??
      (isRead
        ? "prod-db-guard: read runs under a 30s statement_timeout."
        : "prod-db-guard: additive SQL runs under a 30s statement_timeout."),
    updatedInput,
  },
});
