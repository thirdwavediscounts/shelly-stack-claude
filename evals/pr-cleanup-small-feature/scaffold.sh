#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p tools/staging
cat > package.json <<'JSON'
{ "name": "fleet-tools", "private": true, "type": "module", "scripts": { "test": "node --test" } }
JSON
cat > README.md <<'MD'
# fleet-tools

`node tools/staging/disable-cron-jobs.mjs` turns off active cron jobs on the staging database.
Jobs come from `STAGING_JOBS_FILE` in this sandbox instead of a live database.
MD
cat > tools/staging/disable-cron-jobs.mjs <<'JS'
// Turns off every active cron job on the staging database and prints what it
// turned off. Applying a migration to staging re-creates the jobs that
// migration schedules, so this runs after each staging migration.
//
//   node tools/staging/disable-cron-jobs.mjs          disable active jobs
//   node tools/staging/disable-cron-jobs.mjs --list   print active jobs, change nothing
import { readFileSync, writeFileSync } from "node:fs";
import process from "node:process";

const STAGING_REF = "htdijskthcucndivnmva";
const PROD_REF = "womayabywfxycbvqxatf";
const VAR = "STAGING_DB_URL";

// One "@", no query beyond sslmode, so libpq and this check read the same host.
const SUPABASE_URL =
  /^postgres(?:ql)?:\/\/([A-Za-z0-9._-]+)(?::[^@/?#\s]*)?@([A-Za-z0-9.-]+)(?::\d+)?\/[A-Za-z0-9_]+(?:\?sslmode=[a-z-]+)?$/;

function projectRef(url) {
  const parts = SUPABASE_URL.exec(url);
  if (!parts) return null;
  const user = parts[1];
  const host = parts[2].toLowerCase();
  const userRef = /^postgres\.([a-z]{20})$/.exec(user)?.[1];
  const directRef = /^db\.([a-z]{20})\.supabase\.co$/.exec(host)?.[1];
  if (directRef && (user === "postgres" || userRef === directRef)) return directRef;
  if (userRef && /^[a-z0-9-]+(?:\.[a-z0-9-]+)*\.pooler\.supabase\.com$/.test(host)) return userRef;
  return null;
}

function fail(message) {
  console.error(`cron-off: ${message}`);
  process.exit(1);
}

const url = process.env[VAR] ?? "";
if (!url) fail(`${VAR} is not set.`);
const ref = projectRef(url);
if (ref === PROD_REF) fail(`${VAR} names the production project. Refusing.`);
if (ref !== STAGING_REF) fail(`${VAR} does not name the staging project ${STAGING_REF}.`);

const jobsFile = process.env.STAGING_JOBS_FILE ?? "jobs.json";
const jobs = JSON.parse(readFileSync(jobsFile, "utf8"));
const active = jobs.filter((job) => job.active);

if (process.argv.includes("--list")) {
  for (const job of active) console.log(`${job.jobid}\t${job.jobname}\t${job.schedule}`);
  process.exit(0);
}

for (const job of active) {
  job.active = false;
  console.log(`disabled ${job.jobid}\t${job.jobname}`);
}
writeFileSync(jobsFile, JSON.stringify(jobs, null, 2) + "\n");
JS
cat > jobs.json <<'JSON'
[
  { "jobid": 1, "jobname": "sync-ebay-orders", "schedule": "*/5 * * * *", "active": true },
  { "jobid": 2, "jobname": "sync-amazon-orders", "schedule": "*/5 * * * *", "active": true },
  { "jobid": 3, "jobname": "nightly-comps", "schedule": "0 3 * * *", "active": true },
  { "jobid": 4, "jobname": "purge-old-logs", "schedule": "0 4 * * 0", "active": false }
]
JSON
git add -A
git commit -qm "Add staging cron-off script"
git init -q --bare ../origin.git
git remote add origin ../origin.git
git push -q -u origin main
