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
