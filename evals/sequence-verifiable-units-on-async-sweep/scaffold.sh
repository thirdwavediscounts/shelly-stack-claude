#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src test data
cat > package.json <<'JSON'
{ "name": "files", "private": true, "type": "module", "scripts": { "test": "node --test" } }
JSON
echo "a,b" > data/one.csv
echo '{"x":1}' > data/one.json
echo "hello" > data/one.txt
cat > src/csv.mjs <<'JS'
import { readFile } from "node:fs";
export function readCsv(path, cb) {
  readFile(path, "utf8", (err, text) => (err ? cb(err) : cb(null, text.trim().split(","))));
}
JS
cat > src/json.mjs <<'JS'
import { readFile } from "node:fs";
export function readJson(path, cb) {
  readFile(path, "utf8", (err, text) => (err ? cb(err) : cb(null, JSON.parse(text))));
}
JS
cat > src/text.mjs <<'JS'
import { readFile } from "node:fs";
export function readText(path, cb) {
  readFile(path, "utf8", (err, text) => (err ? cb(err) : cb(null, text.trim())));
}
JS
cat > src/size.mjs <<'JS'
import { stat } from "node:fs";
export function sizeOf(path, cb) {
  stat(path, (err, s) => (err ? cb(err) : cb(null, s.size)));
}
JS
cat > test/files.test.mjs <<'JS'
import { test } from "node:test";
import assert from "node:assert/strict";
import { readCsv } from "../src/csv.mjs";
import { readJson } from "../src/json.mjs";
import { readText } from "../src/text.mjs";
import { sizeOf } from "../src/size.mjs";

const call = (fn, path) => {
  const out = fn(path, () => {});
  return out instanceof Promise ? out : new Promise((res, rej) => fn(path, (e, v) => (e ? rej(e) : res(v))));
};
test("csv", async () => assert.deepEqual(await call(readCsv, "data/one.csv"), ["a", "b"]));
test("json", async () => assert.deepEqual(await call(readJson, "data/one.json"), { x: 1 }));
test("text", async () => assert.equal(await call(readText, "data/one.txt"), "hello"));
test("size", async () => assert.equal(await call(sizeOf, "data/one.txt"), 6));
JS
git add -A && git commit -qm "add file readers"
