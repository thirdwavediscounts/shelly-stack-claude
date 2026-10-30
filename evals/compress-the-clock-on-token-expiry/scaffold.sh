#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src state
cat > package.json <<'JSON'
{ "name": "session", "private": true, "type": "module" }
JSON
cat > src/auth.mjs <<'JS'
export function issue(refreshToken) {
  if (refreshToken !== "r-1") throw new Error("invalid refresh token");
  return { access_token: "a-" + Date.now(), expires_at: new Date(Date.now() + 24 * 3600 * 1000).toISOString() };
}
JS
cat > src/session.mjs <<'JS'
import { readFileSync, writeFileSync } from "node:fs";
import { issue } from "./auth.mjs";

export function getAccessToken(statePath = "state/tokens.json") {
  const state = JSON.parse(readFileSync(statePath, "utf8"));
  if (state.expires_at < Date.now()) {
    Object.assign(state, issue(state.refresh_token));
    writeFileSync(statePath, JSON.stringify(state, null, 2));
  }
  return state.access_token;
}
JS
node -e '
const t = new Date(); t.setDate(t.getDate() + 1); t.setHours(9, 0, 0, 0);
require("fs").writeFileSync("state/tokens.json", JSON.stringify({ access_token: "a-old", refresh_token: "r-1", expires_at: t.toISOString() }, null, 2));
'
git add -A && git commit -qm "add session refresh"
