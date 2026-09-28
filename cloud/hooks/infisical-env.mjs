// SessionStart: writes each twd app's env file from Infisical `dev` so cloud sessions can run apps.
// The machine identity has Viewer on the project; only the dev environment is written.
// No-op without INFISICAL_CLIENT_ID, INFISICAL_CLIENT_SECRET and INFISICAL_PROJECT_ID. Prints names only.
import { existsSync, readFileSync, writeFileSync } from "node:fs";

const { INFISICAL_CLIENT_ID: id, INFISICAL_CLIENT_SECRET: secret, INFISICAL_PROJECT_ID: project } = process.env;
if (!id || !secret || !project) process.exit(0);

const API = process.env.INFISICAL_API_URL ?? "https://app.infisical.com/api";
const START = process.env.CLAUDE_PROJECT_DIR ?? process.cwd();
// Cloud sessions start in the folder that holds the clones, so apps/ sits one level down.
const ROOT = !existsSync(`${START}/apps`) && existsSync(`${START}/twd-apps-monorepo/apps`) ? `${START}/twd-apps-monorepo` : START;
const HEADER = "# Written by the shelly-stack infisical-env hook from Infisical dev. Edits are overwritten.";
// Folders whose app loads `.env` or lives in a subdirectory; the rest map to apps/<folder>/.env.local.
const FILES = {
  "argus-console-frontend": "apps/argus-console/frontend/.env",
  "home-frontend": "apps/home/frontend/.env.local",
  "management-kpi": "apps/management-kpi/.env",
  "product-research": "apps/product-research/.env",
};

const fail = (msg) => { console.log(`infisical-env: ${msg}; app env files not written`); process.exit(0); };

const login = await fetch(`${API}/v1/auth/universal-auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ clientId: id, clientSecret: secret }),
}).catch(() => null);
if (!login?.ok) fail(`login failed (${login?.status ?? "network"})`);
const { accessToken } = await login.json();

const query = new URLSearchParams({ workspaceId: project, environment: "dev", secretPath: "/", recursive: "true", expandSecretReferences: "true" });
const res = await fetch(`${API}/v3/secrets/raw?${query}`, { headers: { Authorization: `Bearer ${accessToken}` } }).catch(() => null);
if (!res?.ok) fail(`fetch failed (${res?.status ?? "network"})`);
const { secrets } = await res.json();

const byFolder = {};
for (const s of secrets) (byFolder[s.secretPath.replace(/^\/|\/$/g, "")] ??= {})[s.secretKey] = s.secretValue;
const shared = byFolder[""] ?? {};

const quote = (v) => (/['\n]/.test(v) ? `"${v.replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\n/g, "\\n")}"` : `'${v}'`);
const written = [];
for (const [folder, own] of Object.entries(byFolder)) {
  if (!folder || folder.includes("/")) continue;
  const rel = FILES[folder] ?? `apps/${folder}/.env.local`;
  const dir = `${ROOT}/${rel.slice(0, rel.lastIndexOf("/"))}`;
  const file = `${ROOT}/${rel}`;
  if (!existsSync(dir)) continue;
  if (existsSync(file) && !readFileSync(file, "utf8").startsWith(HEADER)) { written.push(`${rel} (kept, not ours)`); continue; }
  const env = { ...shared, ...own };
  writeFileSync(file, [HEADER, ...Object.entries(env).map(([k, v]) => `${k}=${quote(v)}`)].join("\n") + "\n", { mode: 0o600 });
  written.push(`${rel} (${Object.keys(env).length})`);
}
console.log(`infisical-env: wrote ${written.join(", ")}`);
