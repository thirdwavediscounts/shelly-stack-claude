#!/usr/bin/env bash
# Record a browser drive of one app feature on the local dev server, on the
# current branch, and post the video to the ticket's Slack thread as the
# verify-live step. Prints the control.mjs JSON line. Exit 1 when the drive
# fails; the Slack post still goes out saying what happened.
# Usage: verify-live.sh <TICKET-ID> <app id from scripts/verification/catalog.mjs> <feature slug|/route>
set -u
ticket="${1:?ticket id}"
app="${2:?app id}"
feature="${3:?feature slug or /route}"
repo="${TWD_REPO:-/home/user/twd-apps-monorepo}"
here="$(cd "$(dirname "$0")" && pwd)"
slack="$here/../bin/ticket-slack.mjs"
cd "$repo" || exit 1

# Chromium behind the cloud egress proxy: the proxy rejects TLS 1.3, and the
# session runs as root. The dev server is loopback, so it bypasses the proxy.
if [ -n "${HTTPS_PROXY:-}" ]; then
  export AGENT_BROWSER_ARGS="${AGENT_BROWSER_ARGS:---no-sandbox,--ssl-version-max=tls1.2}"
  export AGENT_BROWSER_PROXY_BYPASS="${AGENT_BROWSER_PROXY_BYPASS:-127.0.0.1,localhost}"
fi

bash "$here/materialize.sh" "$repo"
# agent-browser records through ffmpeg; the base image lacks it.
command -v ffmpeg >/dev/null 2>&1 || apt-get install -y --no-install-recommends ffmpeg >/dev/null 2>&1 || true

post() { node "$slack" post "$ticket" verify-live "$1" "${@:2}"; }

if ! start=$(node scripts/verification/dev-server.mjs start "$app" 2>&1); then
  reason=$(printf '%s' "$start" | tail -1)
  post "\`$app\` dev server did not start, so there is no recording. $reason"
  echo "{\"error\":\"dev server failed to start\"}"
  exit 1
fi

result=$(node scripts/verification/control.mjs verify "$app" "$feature" --local --record 2>/dev/null | tail -1)
node scripts/verification/control.mjs close "$app" >/dev/null 2>&1
node scripts/verification/dev-server.mjs stop "$app" >/dev/null 2>&1

video="artifacts/verification/$app/runtime/control-proof.webm"
read -r authed errors heading <<<"$(node -e '
  const r = JSON.parse(process.argv[1] || "{}");
  console.log(r.authed ? "yes" : "no", Number(r.errors || 0), JSON.stringify(r.heading || r.error || ""));
' "$result")"

if [ -s "$video" ] && [ "$authed" = yes ]; then
  post "\`$app\` · \`$feature\` · authed yes · $errors page errors · heading $heading
Recorded on the local dev server with the branch checked out." --file "$video"
  echo "$result"
  exit 0
fi

post "\`$app\` · \`$feature\` · authed $authed · $errors page errors · heading $heading
No usable recording. Result: \`$result\`"
echo "$result"
exit 1
