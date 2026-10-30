#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p workers
cat > package.json <<'JSON'
{ "name": "workers", "private": true, "type": "module" }
JSON
echo '{}' > state.json
cat > workers/update.mjs <<'JS'
import { readFile, writeFile } from "node:fs/promises";

export async function updateState(field, value) {
  const state = JSON.parse(await readFile("state.json", "utf8"));
  await new Promise((r) => setTimeout(r, 20));
  state[field] = value;
  await writeFile("state.json", JSON.stringify(state, null, 2));
}
JS
cat > workers/indexer.mjs <<'JS'
import { updateState } from "./update.mjs";
export const runIndexer = () => updateState("indexerLastRun", new Date().toISOString());
JS
cat > workers/metrics.mjs <<'JS'
import { updateState } from "./update.mjs";
export const runMetrics = () => updateState("metricsLastRun", new Date().toISOString());
JS
cat > run-both.mjs <<'JS'
import { readFileSync, writeFileSync } from "node:fs";
import { runIndexer } from "./workers/indexer.mjs";
import { runMetrics } from "./workers/metrics.mjs";

writeFileSync("state.json", "{}");
await Promise.all([runIndexer(), runMetrics()]);
console.log(readFileSync("state.json", "utf8"));
JS
git add -A && git commit -qm "add workers"
