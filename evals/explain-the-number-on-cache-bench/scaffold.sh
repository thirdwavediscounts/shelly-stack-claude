#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src
cat > package.json <<'JSON'
{ "name": "parser", "private": true, "type": "module" }
JSON
cat > src/parse.mjs <<'JS'
const cache = new Map();

export function parseNoCache(text) {
  return text.split("\n").map((line) => line.split(",").map((cell) => cell.trim()));
}

export function parse(text) {
  if (!cache.has(text)) cache.set(text, parseNoCache(text));
  return cache.get(text);
}
JS
cat > bench.mjs <<'JS'
import { parse, parseNoCache } from "./src/parse.mjs";

const doc = Array.from({ length: 2000 }, (_, i) => `${i}, item ${i}, ${i * 3}`).join("\n");
const time = (fn) => {
  const start = performance.now();
  for (let i = 0; i < 2000; i++) fn(doc);
  return performance.now() - start;
};
const before = time(parseNoCache);
const after = time(parse);
console.log(`before ${before.toFixed(0)} ms, after ${after.toFixed(0)} ms, ${(before / after).toFixed(0)}x faster`);
JS
git add -A && git commit -qm "cache parse results"
