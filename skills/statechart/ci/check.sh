#!/bin/sh
set -eu
here=$(cd "$(dirname "$0")" && pwd)
out=$(mktemp -d)
run() {
  code=0
  "$here/../scripts/statechart" "$here/NellisPutBack.tla" --config "$here/$1.cfg" --view "$here/view.mjs" --out "$out/$1" >/dev/null || code=$?
  [ "$code" -eq "$2" ] || { echo "$1: exit $code, want $2" >&2; cat "$out/$1/report.md" >&2 2>/dev/null; exit 1; }
}
run old 1
grep -q '^## PutBackFollowsJudge breaks' "$out/old/report.md"
grep -q '3. the judge changes its call' "$out/old/report.md"
run new 0
grep -q 'PutBackFollowsJudge, NoDeadlock' "$out/new/report.md"
grep -q 'you put the comp back' "$out/new/chart.mmd"
echo "statechart ok"
