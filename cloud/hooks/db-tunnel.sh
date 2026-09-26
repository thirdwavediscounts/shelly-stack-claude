#!/bin/bash
# SessionStart: cloud egress allows only HTTP(S) through a proxy, so direct Postgres
# (5432/6543) is blocked. Forward each DB host:port the app env files use over `ssh twd`
# and point the host at a loopback address in /etc/hosts. The hostname is unchanged, so
# TLS still verifies. Backgrounds itself; no-op without tailscale or env files.
[ -n "${TS_AUTHKEY:-}" ] && command -v ssh >/dev/null 2>&1 || exit 0
ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
LOG=/tmp/db-tunnel.log

run() {
  # Wait for tailscale-up.sh and infisical-env.mjs, which run alongside this hook.
  for _ in $(seq 1 60); do
    tailscale --socket=/tmp/tailscaled.sock status >/dev/null 2>&1 \
      && ls "$ROOT"/apps/*/.env.local >/dev/null 2>&1 && break
    sleep 1
  done
  # host:port pairs from postgres URLs; prints no credentials.
  mapfile -t pairs < <(find "$ROOT"/apps -maxdepth 3 -name '.env*' ! -name '*.example' -type f \
    -not -path '*/node_modules/*' -exec cat {} + 2>/dev/null \
    | grep -oE "postgres(ql)?://[^@[:space:]'\"]+@[^:/?[:space:]'\"]+(:[0-9]+)?" \
    | sed -E 's|.*@||; /:[0-9]+$/!s|$|:5432|' | sort -u)
  [ ${#pairs[@]} -gt 0 ] || { echo "no postgres hosts found" >>"$LOG"; return; }

  local -A addr; local n=1 forwards=() host port
  for pair in "${pairs[@]}"; do
    host=${pair%:*} port=${pair##*:}
    if [ -z "${addr[$host]:-}" ]; then
      addr[$host]="127.0.0.$n"; n=$((n + 1))
      sed -i "/[[:space:]]$host\$/d" /etc/hosts
      echo "${addr[$host]} $host" >>/etc/hosts
    fi
    forwards+=(-L "${addr[$host]}:$port:$host:$port")
  done
  echo "forwarding ${pairs[*]}" >>"$LOG"
  while true; do
    ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=15 -o ServerAliveCountMax=3 \
      "${forwards[@]}" twd >>"$LOG" 2>&1
    echo "ssh exited $?, retrying in 5s" >>"$LOG"
    sleep 5
  done
}

PID=/tmp/db-tunnel.pid
[ -f $PID ] && kill -0 "$(cat $PID)" 2>/dev/null && exit 0
export -f run; export ROOT LOG
setsid nohup bash -c run >/dev/null 2>&1 </dev/null &
echo $! >$PID
echo "db-tunnel: forwarding Postgres over ssh twd in the background (log $LOG)"
