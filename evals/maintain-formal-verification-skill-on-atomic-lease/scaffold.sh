#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src
cat > package.json <<'JSON'
{ "name": "workers", "private": true, "type": "module" }
JSON
cat > src/lease.mjs <<'JS'
export async function acquire(store, worker) {
  const holder = await store.get("lease");
  if (holder === undefined) {
    await store.set("lease", worker);
    return true;
  }
  return false;
}

export async function release(store, worker) {
  if ((await store.get("lease")) === worker) await store.delete("lease");
}
JS
cat > src/store.mjs <<'JS'
export function memoryStore() {
  const data = new Map();
  const tick = () => new Promise((r) => setImmediate(r));
  return {
    async get(key) { await tick(); return data.get(key); },
    async set(key, value) { await tick(); data.set(key, value); },
    async setIfAbsent(key, value) { await tick(); if (data.has(key)) return false; data.set(key, value); return true; },
    async delete(key) { await tick(); data.delete(key); },
  };
}
JS
git add -A && git commit -qm "add lease for the sync workers"

mkdir -p check .claude/skills/lease-race
cat > check/lease-model.mjs <<'JS'
const STEPS = ["read", "write"];

function explore(state, pcs, trace, found) {
  const done = pcs.every((pc) => pc === STEPS.length);
  if (done) {
    if (state.holders.length > 1) found.push(trace);
    return;
  }
  pcs.forEach((pc, w) => {
    if (pc === STEPS.length) return;
    const next = { lease: state.lease, seen: [...state.seen], holders: [...state.holders] };
    if (STEPS[pc] === "read") next.seen[w] = next.lease;
    else if (next.seen[w] === undefined) { next.lease = w; next.holders.push(w); }
    const nextPcs = [...pcs];
    nextPcs[w]++;
    explore(next, nextPcs, [...trace, `worker ${w} ${STEPS[pc]}s the lease`], found);
  });
}

const found = [];
explore({ lease: undefined, seen: [], holders: [] }, [0, 0], [], found);
if (found.length) {
  console.log("FAIL: two workers hold the lease");
  console.log(found[0].join("\n"));
  process.exit(1);
}
console.log("PASS: at most one worker holds the lease");
JS
cat > .claude/skills/lease-race/SKILL.md <<TXT
---
name: lease-race
description: Model-check the lease in src/lease.mjs for two workers holding it at once. Use when a change touches src/lease.mjs or src/store.mjs.
---

# Lease race

Covers acquire() in src/lease.mjs. The model in check/lease-model.mjs treats each store call as one step: get is "read", set is "write".

Run: node check/lease-model.mjs

Synced at commit $(git rev-parse HEAD). Move this forward only after you confirm the model describes the code at the new commit.

Known finding at the sync commit: two workers can both read an empty lease and both write it.
TXT
git add -A && git commit -qm "add lease model check"
cat > src/lease.mjs <<'JS'
export async function acquire(store, worker) {
  return store.setIfAbsent("lease", worker);
}

export async function release(store, worker) {
  if ((await store.get("lease")) === worker) await store.delete("lease");
}
JS
git commit -qam "fix: take the lease with one atomic setIfAbsent"
