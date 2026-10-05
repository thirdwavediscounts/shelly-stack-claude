#!/usr/bin/env bash
# Drives template.sh's example stage through a real terminal (expect) in a sandbox
# with stub browser and vercel commands. Exits non-zero on the first failed check.
set -euo pipefail

TEMPLATE="$(cd "$(dirname "$0")" && pwd)/template.sh"
SB="$(mktemp -d)"
trap 'rm -rf "$SB"' EXIT
fail() { echo "FAIL: $*"; exit 1; }

mkdir -p "$SB/bin" "$SB/work"
for cmd in open xdg-open; do
  printf '#!/bin/bash\necho "open $*" >> %s/calls.log\n' "$SB" > "$SB/bin/$cmd"
done
printf '#!/bin/bash\necho "vercel $* | stdin=$(cat)" >> %s/calls.log\n' "$SB" > "$SB/bin/vercel"
chmod +x "$SB/bin/"*

for term in dumb xterm-256color; do
  : > "$SB/calls.log"
  printf 'UNRELATED=keep-me\n' > "$SB/work/.env"
  cat > "$SB/drive.exp" <<EOF
set timeout 10
log_file -noappend $SB/terminal.log
proc run {answers} {
  spawn env PATH=$SB/bin:/usr/bin:/bin TERM=$term ENV_FILE=$SB/work/.env bash $TEMPLATE
  foreach {pat ans} \$answers {
    expect {
      -re \$pat { send -- "\$ans\r" }
      timeout { puts "TIMEOUT waiting for: \$pat"; exit 9 }
      eof { puts "EOF before: \$pat"; exit 8 }
    }
  }
  expect eof
  catch wait result
  if {[lindex \$result 3] != 0} { puts "EXIT [lindex \$result 3]"; exit 7 }
}
run {"Ready to start" "" "Paste the App ID" "app-id-1" "Paste the Cert ID" "cert-secret-1" "Vercel project for production" "y"}
run {"Ready to start" "" "Paste the App ID" "" "Paste the Cert ID" "" "Vercel project for production" "n"}
EOF
  expect "$SB/drive.exp" > "$SB/expect.out" 2>&1 || fail "TERM=$term: $(tail -n 3 "$SB/expect.out")"

  [[ "$(grep -cxF UNRELATED=keep-me "$SB/work/.env")" == 1 ]] || fail "TERM=$term: existing line lost"
  [[ "$(grep -cxF EBAY_CLIENT_ID=app-id-1 "$SB/work/.env")" == 1 ]] || fail "TERM=$term: App ID not written once"
  [[ "$(grep -cxF EBAY_CLIENT_SECRET=cert-secret-1 "$SB/work/.env")" == 1 ]] || fail "TERM=$term: Cert ID not written once"
  [[ "$(wc -l < "$SB/work/.env" | tr -d ' ')" == 3 ]] || fail "TERM=$term: re-run duplicated lines"
  [[ "$(grep -c '^open ' "$SB/calls.log")" == 2 ]] || fail "TERM=$term: expected one browser open per run"
  [[ "$(grep -c '^vercel env add ' "$SB/calls.log")" == 2 ]] || fail "TERM=$term: expected two vercel calls on the first run only"
  grep -q 'stdin=cert-secret-1$' "$SB/calls.log" || fail "TERM=$term: secret did not reach vercel through stdin"
  ! sed 's/ | stdin=.*//' "$SB/calls.log" | grep -q cert-secret-1 || fail "TERM=$term: secret leaked into vercel argv"
  ! grep -aq cert-secret-1 "$SB/terminal.log" || fail "TERM=$term: secret echoed to the terminal"
  echo "ok TERM=$term"
done
