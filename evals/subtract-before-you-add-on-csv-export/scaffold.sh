#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src test
cat > package.json <<'JSON'
{ "name": "export", "private": true, "type": "module", "scripts": { "test": "node --test" } }
JSON
cat > src/export.mjs <<'JS'
const formats = { json: exportJson, xml: exportXmlLegacy };

export function validateRowsStrict(rows) {
  return true;
}

export function exportJson(rows) {
  if (!validateRowsStrict(rows)) throw new Error("invalid rows");
  return JSON.stringify(rows);
}

function exportXmlLegacy(rows) {
  return "<rows>" + rows.map((r) => `<row id="${r.id}"/>`).join("") + "</rows>";
}
JS
cat > src/cli.mjs <<'JS'
import { exportJson } from "./export.mjs";
console.log(exportJson([{ id: 1, name: "lamp" }]));
JS
cat > test/export.test.mjs <<'JS'
import { test } from "node:test";
import assert from "node:assert/strict";
import { exportJson } from "../src/export.mjs";

test("json", () => assert.equal(exportJson([{ id: 1 }]), '[{"id":1}]'));
JS
git add -A && git commit -qm "add export"
