#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src
cat > package.json <<'JSON'
{ "name": "importer", "private": true, "type": "module" }
JSON
echo '{ "batchSize": 50 }' > config.json
cat > src/config.mjs <<'JS'
import { readFileSync } from "node:fs";
export const loadConfig = (path = "config.json") => JSON.parse(readFileSync(path, "utf8"));
JS
cat > src/import.mjs <<'JS'
export async function importOrders(cfg, rows, send) {
  if (!cfg || typeof cfg.batchSize !== "number") throw new Error("bad config: batchSize");
  for (let i = 0; i < rows.length; i += cfg.batchSize) {
    await send(rows.slice(i, i + cfg.batchSize));
  }
}
JS
cat > src/sync.mjs <<'JS'
import { loadConfig } from "./config.mjs";
import { importOrders } from "./import.mjs";

export async function sync(rows, send) {
  const cfg = loadConfig();
  if (!cfg || typeof cfg.batchSize !== "number") throw new Error("bad config: batchSize");
  await importOrders(cfg, rows, send);
}
JS
git add -A && git commit -qm "add importer"
