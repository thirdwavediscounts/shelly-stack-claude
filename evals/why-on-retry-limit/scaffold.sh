#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src
cat > package.json <<'JSON'
{ "name": "sync", "private": true, "type": "module" }
JSON
cat > src/fetch-retry.mjs <<'JS'
const RETRYABLE = (status) => status === 429 || status >= 500;

export async function fetchWithRetry(request, { attempts = 3, baseMs = 200, sleep = (ms) => new Promise((r) => setTimeout(r, ms)) } = {}) {
  let response;
  for (let attempt = 0; attempt < attempts; attempt++) {
    response = await request();
    if (!RETRYABLE(response.status)) return response;
    const wait = baseMs * 2 ** attempt;
    await sleep(wait / 2 + Math.random() * (wait / 2));
  }
  return response;
}
JS
git add -A && git commit -qm "add fetchWithRetry with 3 attempts"
sed -i.bak 's/attempts = 3/attempts = 5/' src/fetch-retry.mjs && rm src/fetch-retry.mjs.bak
git commit -qam "raise retry limit to 5" -m "Temu returns bursts of 429 during the 9pm order sync. With 3 attempts we dropped about 4% of orders on 2026-10-02. Five attempts with jittered backoff spans about 6 seconds, which covers the bursts we logged."
