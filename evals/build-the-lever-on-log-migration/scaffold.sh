#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src/jobs test
cat > package.json <<'JSON'
{ "name": "jobs", "private": true, "type": "module", "scripts": { "test": "node --test" } }
JSON
cat > src/log.mjs <<'JS'
export const lines = [];
export const log = { info: (msg) => lines.push(msg) };
export const oldLog = (msg) => lines.push(msg);
JS
for i in $(seq -w 1 30); do
cat > src/jobs/job$i.mjs <<JS
import { oldLog } from "../log.mjs";

export function job$i() {
  oldLog("job$i start");
  const n = $((10#$i)) * 2;
  oldLog("job$i computed " + n);
  return n;
}
JS
done
cat > test/jobs.test.mjs <<'JS'
import { test } from "node:test";
import assert from "node:assert/strict";
import { lines } from "../src/log.mjs";
import { job07 } from "../src/jobs/job07.mjs";

test("job07 logs", () => {
  assert.equal(job07(), 14);
  assert.deepEqual(lines, ["job07 start", "job07 computed 14"]);
});
JS
git add -A && git commit -qm "add jobs"
