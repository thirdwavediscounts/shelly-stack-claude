#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p scripts tmp
cat > package.json <<'JSON'
{ "name": "ops", "private": true, "type": "module" }
JSON
cat > scripts/cleanup.mjs <<'JS'
import { readdirSync, statSync, rmSync } from "node:fs";
import { join } from "node:path";

const dir = process.argv[2] ?? "tmp";
const cutoff = Date.now() - 7 * 24 * 3600 * 1000;

for (const name of readdirSync(dir)) {
  const path = join(dir, name);
  if (statSync(path).mtimeMs < cutoff) {
    rmSync(path, { recursive: true });
    console.log(`deleted ${path}`);
  }
}
JS
touch -t 202601010000 tmp/old.log
touch tmp/new.log
git add -A && git commit -qm "add cleanup script"
