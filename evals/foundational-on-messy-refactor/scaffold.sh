#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src
cat > package.json <<'JSON'
{ "name": "auctions", "private": true, "type": "module", "scripts": { "test": "node --test" } }
JSON
cat > src/ending.mjs <<'JS'
export function endingSoon(auctions) {
  const out = [];
  for (const a of auctions) {
    const left = (new Date(a.end_time) - new Date()) / 3600000;
    if (left > 0 && left < 24 && a.status !== "ended" && a.status !== "cancelled") out.push(a);
  }
  return out;
}
JS
cat > src/watchlist.mjs <<'JS'
export function watchlist(auctions, ids) {
  const out = [];
  for (const a of auctions) {
    if (!ids.includes(a.id)) continue;
    const hoursLeft = (Date.parse(a.end_time) - Date.now()) / 1000 / 60 / 60;
    if (hoursLeft <= 0) continue;
    if (a.status == "ended" || a.status == "cancelled") continue;
    out.push({ ...a, hoursLeft });
  }
  return out;
}
JS
cat > src/report.mjs <<'JS'
export function report(auctions) {
  let live = 0;
  for (const a of auctions) {
    const h = (new Date(a.end_time).getTime() - Date.now()) / 3.6e6;
    if (h > 0 && !["ended", "cancelled"].includes(a.status)) live++;
  }
  return `${live} live auctions`;
}
JS
cat > src/auctions.test.mjs <<'JS'
import { test } from "node:test";
import assert from "node:assert/strict";
import { endingSoon } from "./ending.mjs";
import { watchlist } from "./watchlist.mjs";
import { report } from "./report.mjs";

const soon = new Date(Date.now() + 3600000).toISOString();
const later = new Date(Date.now() + 48 * 3600000).toISOString();
const auctions = [
  { id: 1, end_time: soon, status: "live" },
  { id: 2, end_time: later, status: "live" },
  { id: 3, end_time: soon, status: "cancelled" },
];

test("ending soon", () => assert.deepEqual(endingSoon(auctions).map((a) => a.id), [1]));
test("watchlist", () => assert.deepEqual(watchlist(auctions, [2, 3]).map((a) => a.id), [2]));
test("report", () => assert.equal(report(auctions), "2 live auctions"));
JS
git add -A && git commit -qm "add auction helpers"
