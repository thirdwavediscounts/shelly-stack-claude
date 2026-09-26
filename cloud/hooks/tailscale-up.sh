#!/bin/bash
# SessionStart: joins the tailnet so `ssh twd` reaches the Argus box.
# No-op without TS_AUTHKEY or tailscale (the setup script installs both it and the ssh config).
[ -n "${TS_AUTHKEY:-}" ] && command -v tailscale >/dev/null 2>&1 || exit 0
SOCK=/tmp/tailscaled.sock
tailscale --socket=$SOCK status >/dev/null 2>&1 && exit 0
setsid nohup tailscaled --tun=userspace-networking --state=mem: --socket=$SOCK \
  >/tmp/tailscaled.log 2>&1 < /dev/null &
for _ in $(seq 1 20); do [ -S $SOCK ] && break; sleep 0.5; done
tailscale --socket=$SOCK up --authkey="$TS_AUTHKEY" \
  --hostname="claude-cloud-$(hostname | cut -c1-8)" >>/tmp/tailscaled.log 2>&1 || true
exit 0
