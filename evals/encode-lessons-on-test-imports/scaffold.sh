#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src test
cat > package.json <<'JSON'
{ "name": "report", "private": true, "type": "module", "scripts": { "test": "node --test" } }
JSON
cat > test/fixtures.mjs <<'JS'
export const sampleOrders = [{ id: 1, total: 20 }, { id: 2, total: 5 }];
export const sum = (orders) => orders.reduce((s, o) => s + o.total, 0);
JS
cat > src/report.mjs <<'JS'
import { sum } from "../test/fixtures.mjs";
export const report = (orders) => `orders: ${orders.length}, total: ${sum(orders)}`;
JS
cat > test/report.test.mjs <<'JS'
import { test } from "node:test";
import assert from "node:assert/strict";
import { report } from "../src/report.mjs";
import { sampleOrders } from "./fixtures.mjs";

test("report", () => assert.equal(report(sampleOrders), "orders: 2, total: 25"));
JS
git add -A && git commit -qm "add report"
