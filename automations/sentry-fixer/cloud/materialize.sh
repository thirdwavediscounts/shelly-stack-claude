#!/usr/bin/env bash
# Cloud only. Turn the environment's secrets into the files local sessions
# already have: the verify-live creds and the Infisical .env exports. The setup
# script cannot do this, it runs before the env vars exist and is snapshot
# cached. Every step is gated on its env var, so it no-ops locally. Prints
# sizes and counts only, never a value.
# Usage: materialize.sh [repo root, default /home/user/twd-apps-monorepo]
set -u
repo="${1:-/home/user/twd-apps-monorepo}"
out=()

if [ -n "${VERIFY_LIVE_CREDS:-}" ]; then
  d=~/.claude/private/verify-live
  mkdir -p "$d" && chmod 700 "$d"
  printf '%s\n' "$VERIFY_LIVE_CREDS" > "$d/creds.json" && chmod 600 "$d/creds.json"
  out+=("creds.json $(wc -c < "$d/creds.json" | tr -d ' ')B")
fi

if [ -n "${INFISICAL_CLIENT_ID:-}" ]; then
  if ! command -v infisical >/dev/null 2>&1; then
    out+=(".env SKIPPED: infisical CLI missing")
  else
    tok=$(infisical login --method=universal-auth --client-id="$INFISICAL_CLIENT_ID" \
      --client-secret="${INFISICAL_CLIENT_SECRET:-}" --plain --silent 2>/dev/null || true)
    if [ -z "$tok" ]; then
      out+=(".env FAILED: infisical login refused")
    else
      for pair in "/:.env" "/product-research:apps/product-research/.env" "/argus-console-frontend:apps/argus-console/frontend/.env"; do
        folder="${pair%%:*}"
        file="$repo/${pair#*:}"
        if INFISICAL_TOKEN="$tok" infisical export --projectId="${INFISICAL_PROJECT_ID:-}" --env=dev \
            --path="$folder" --format=dotenv > "$file.tmp" 2>/dev/null && [ -s "$file.tmp" ]; then
          mv "$file.tmp" "$file" && chmod 600 "$file"
          out+=("${pair#*:} $(grep -c '^[A-Za-z_][A-Za-z0-9_]*=' "$file") keys")
        else
          rm -f "$file.tmp"
          out+=("${pair#*:} FAILED")
        fi
      done
    fi
    unset tok
  fi
fi

printf 'materialize: %s\n' "${out[*]:-nothing to do}"
