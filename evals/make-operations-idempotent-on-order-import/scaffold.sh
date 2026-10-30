#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src data/incoming data/processed
cat > package.json <<'JSON'
{ "name": "orders", "private": true, "type": "module" }
JSON
echo '[]' > data/orders.json
echo '[{ "id": "o-1", "total": 20 }, { "id": "o-2", "total": 35 }]' > data/incoming/batch-1.json
cat > src/importOrders.mjs <<'JS'
import { readdirSync, readFileSync, writeFileSync, renameSync } from "node:fs";

export function importOrders({ crashAfterWrite = false } = {}) {
  for (const name of readdirSync("data/incoming")) {
    const batch = JSON.parse(readFileSync(`data/incoming/${name}`, "utf8"));
    const orders = JSON.parse(readFileSync("data/orders.json", "utf8"));
    orders.push(...batch);
    writeFileSync("data/orders.json", JSON.stringify(orders, null, 2));
    if (crashAfterWrite) throw new Error("crashed before moving " + name);
    renameSync(`data/incoming/${name}`, `data/processed/${name}`);
  }
}
JS
git add -A && git commit -qm "add order import"
