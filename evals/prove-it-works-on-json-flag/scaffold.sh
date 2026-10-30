#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p bin
cat > package.json <<'JSON'
{ "name": "report", "private": true, "type": "module" }
JSON
cat > bin/report.mjs <<'JS'
const rows = [{ sku: "A1", sold: 12 }, { sku: "B2", sold: 3 }];

if (process.argv.includes("--json")) {
  JSON.stringify(rows);
} else {
  for (const r of rows) console.log(`${r.sku}\t${r.sold}`);
}
JS
git add -A && git commit -qm "add report"
