#!/usr/bin/env node
// ticket-slack — post a ticket's lifecycle events into a single Slack thread.
//
// One Slack app; each step posts under its own name/avatar (chat:write.customize),
// so the thread reads like a relay of bots (orchestrate → fix → verify → ship).
// Thread state is derived by scanning channel history for the ticket's anchor
// message — no database, idempotent, and it survives across cloud sessions.
//
// Usage:
//   ticket-slack.mjs post <TICKET> <step> "<text>" [--file <path>] [--file-title "<t>"]
//   ticket-slack.mjs anchor <TICKET> "<title>"        # idempotent; prints thread ts
//   ticket-slack.mjs thread-ts <TICKET>               # prints existing ts or empty
//
// <step> ∈ start|triage|build|verify|verify-live|pr|ci|blocked|merged (drives identity).
// "start"/"anchor" create the root message; every other step replies in-thread.
//
// Env: SLACK_TICKET_BOT_TOKEN (xoxb-…, scopes chat:write, chat:write.customize,
//      files:write, channels:history) and SLACK_TICKET_CHANNEL (C…).
// If either is unset the tool is a silent no-op (exit 0) so local /work runs skip Slack.
// DRY=1 prints the requests it would make instead of calling Slack (offline check).

import { readFileSync, statSync } from "node:fs";
import { basename } from "node:path";

const TOKEN = process.env.SLACK_TICKET_BOT_TOKEN;
const CHANNEL = process.env.SLACK_TICKET_CHANNEL;
const DRY = process.env.DRY === "1";

// Cat avatars: each step posts as its own bot name with a pinned clean cat photo
// (cataas.com, a public cat-image API). Slack fetches + caches the icon_url per
// URL, so each step keeps its consistent cat. Swap an id below to change a cat.
const cat = (id) => `https://cataas.com/cat/${id}`;

const IDENTITY = {
  start: { username: "orchestrate", icon_url: cat("G2gU9xo3HUvi70LL") },
  triage: { username: "triage", icon_url: cat("CyHhy2hqLNBoraUt") },
  build: { username: "fix", icon_url: cat("C5Ddbc1ilh45jiAk") },
  verify: { username: "verify", icon_url: cat("0M0Lo3dsYft79xNd") },
  "verify-live": { username: "verify-live", icon_url: cat("DDnc0SqHG6mI24cM") },
  pr: { username: "open-pr", icon_url: cat("7U01QMCY91SvOpyk") },
  ci: { username: "ci", icon_url: cat("FAkFJCfYbZOF8aDI") },
  blocked: { username: "blocked", icon_url: cat("8Tx4SPtXlW9TR5Lm") },
  merged: { username: "ship", icon_url: cat("7aqq2nCe7IiZEKjJ") },
};
const ROOT_STEPS = new Set(["start", "anchor"]);

function die(msg) {
  process.stderr.write(`ticket-slack: ${msg}\n`);
  process.exit(1);
}

// Ticket token, e.g. DEV-165, matched as a whole word inside the anchor text.
function ticketRe(ticket) {
  return new RegExp(`\\b${ticket.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`);
}

async function slack(method, payload, { form = false } = {}) {
  const url = `https://slack.com/api/${method}`;
  if (DRY) {
    process.stderr.write(`DRY ${method} ${JSON.stringify(payload)}\n`);
    // Minimal shapes so downstream logic runs in dry mode.
    if (method === "conversations.history") return { ok: true, messages: [] };
    if (method === "chat.postMessage") return { ok: true, ts: "0000.0000", channel: CHANNEL };
    if (method === "files.getUploadURLExternal")
      return { ok: true, upload_url: "https://dry.invalid/upload", file_id: "DRYFILE" };
    return { ok: true };
  }
  const headers = { Authorization: `Bearer ${TOKEN}` };
  let body;
  if (form) {
    body = new URLSearchParams(payload).toString();
    headers["Content-Type"] = "application/x-www-form-urlencoded";
  } else {
    body = JSON.stringify(payload);
    headers["Content-Type"] = "application/json; charset=utf-8";
  }
  const resp = await fetch(url, { method: "POST", headers, body, signal: AbortSignal.timeout(20000) });
  const json = await resp.json().catch(() => ({ ok: false, error: `bad json (${resp.status})` }));
  if (!json.ok) die(`${method} failed: ${json.error || resp.status}`);
  return json;
}

// Find the root (non-reply) message whose text names this ticket; return its ts.
async function findThreadTs(ticket) {
  const re = ticketRe(ticket);
  let cursor;
  for (let page = 0; page < 5; page++) {
    const q = { channel: CHANNEL, limit: "100" };
    if (cursor) q.cursor = cursor;
    const res = await slack("conversations.history", q, { form: true });
    for (const m of res.messages || []) {
      const isRoot = !m.thread_ts || m.thread_ts === m.ts;
      if (isRoot && typeof m.text === "string" && re.test(m.text)) return m.ts;
    }
    cursor = res.response_metadata?.next_cursor;
    if (!cursor) break;
  }
  return null;
}

async function postMessage({ text, step, thread_ts }) {
  const id = IDENTITY[step] || IDENTITY.start;
  const res = await slack("chat.postMessage", {
    channel: CHANNEL,
    text,
    mrkdwn: true,
    ...(thread_ts ? { thread_ts } : {}),
    ...id,
  });
  return res.ts;
}

// Slack external-upload flow: reserve URL → PUT bytes → complete into the thread.
async function uploadFile({ path, title, thread_ts, comment }) {
  const size = statSync(path).size;
  const filename = basename(path);
  const up = await slack(
    "files.getUploadURLExternal",
    { filename, length: String(size) },
    { form: true },
  );
  if (!DRY) {
    const bytes = readFileSync(path);
    const put = await fetch(up.upload_url, {
      method: "POST",
      body: bytes,
      signal: AbortSignal.timeout(120000),
    });
    if (!put.ok) die(`file PUT failed: ${put.status}`);
  }
  await slack("files.completeUploadExternal", {
    files: JSON.stringify([{ id: up.file_id, title: title || filename }]),
    channel_id: CHANNEL,
    ...(thread_ts ? { thread_ts } : {}),
    ...(comment ? { initial_comment: comment } : {}),
  }, { form: true });
}

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--file") out.file = argv[++i];
    else if (a === "--file-title") out.fileTitle = argv[++i];
    else out._.push(a);
  }
  return out;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const [cmd, ticket, ...rest] = args._;
  if (!cmd) die("usage: ticket-slack.mjs post|anchor|thread-ts <TICKET> …");
  if (!TOKEN || !CHANNEL) process.exit(0); // silent no-op when unconfigured

  if (cmd === "thread-ts") {
    if (!ticket) die("thread-ts needs a TICKET");
    const ts = await findThreadTs(ticket);
    if (ts) process.stdout.write(ts + "\n");
    return;
  }

  if (cmd === "anchor") {
    if (!ticket) die("anchor needs a TICKET");
    const title = rest.join(" ");
    const existing = await findThreadTs(ticket);
    if (existing) {
      process.stdout.write(existing + "\n");
      return;
    }
    const ts = await postMessage({ step: "start", text: `*${ticket}* — ${title || "starting"}` });
    process.stdout.write(ts + "\n");
    return;
  }

  if (cmd === "post") {
    const step = ticket ? rest[0] : null;
    const text = rest.slice(1).join(" ");
    if (!ticket || !step) die("usage: ticket-slack.mjs post <TICKET> <step> \"<text>\" [--file …]");
    if (!IDENTITY[step]) die(`unknown step "${step}" (want ${Object.keys(IDENTITY).join("|")})`);

    let thread_ts = await findThreadTs(ticket);
    if (!thread_ts) {
      // No anchor yet — create one so no event is ever orphaned. A root step
      // (start/anchor) uses its own text as the title; otherwise a generic one.
      const title = ROOT_STEPS.has(step) && text ? text : "run started";
      thread_ts = await postMessage({ step: "start", text: `*${ticket}* — ${title}` });
    }
    // For root steps the anchor already exists; only reply for non-root steps.
    if (!ROOT_STEPS.has(step)) {
      await postMessage({ step, text, thread_ts });
    }
    if (args.file) {
      await uploadFile({
        path: args.file,
        title: args.fileTitle || `${ticket} ${step}`,
        thread_ts,
        comment: `:movie_camera: ${text || "evidence"}`,
      });
    }
    return;
  }

  die(`unknown command "${cmd}"`);
}

main().catch((e) => die(e?.message || String(e)));
