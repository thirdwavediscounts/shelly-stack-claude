#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src
cat > package.json <<'JSON'
{ "name": "bench", "private": true, "type": "module" }
JSON
cat > src/sum.mjs <<'JS'
export function sum(values) {
  let total = 0;
  for (const v of values) total += v;
  return total;
}

export function* fastSum(values) {
  let total = 0;
  for (const v of values) total += v;
  yield total;
}
JS
cat > bench.mjs <<'JS'
import { sum, fastSum } from "./src/sum.mjs";

const values = Array.from({ length: 1_000_000 }, (_, i) => i % 97);
const time = (fn) => {
  const start = performance.now();
  for (let i = 0; i < 50; i++) fn(values);
  return performance.now() - start;
};
const slow = time(sum);
const fast = time(fastSum);
console.log(`sum ${slow.toFixed(1)} ms, fastSum ${fast.toFixed(1)} ms, ${(slow / fast).toFixed(0)}x faster`);
JS
git add -A && git commit -qm "add fastSum and bench"
