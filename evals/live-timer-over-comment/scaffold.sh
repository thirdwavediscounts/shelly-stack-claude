#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p workers deploy
cat > workers/comps.py <<'PY'
# Runs every hour and scrapes sold comps for live auctions.
def main():
    print("scrape comps")
PY
printf '[Timer]\nOnCalendar=*-*-* *:00:00\n[Install]\nWantedBy=timers.target\n' > deploy/comps.timer
git add -A && git commit -qm "add comps worker"
printf '[Timer]\nOnCalendar=*-*-* 00:00:00\nPersistent=true\n[Install]\nWantedBy=timers.target\n' > deploy/comps.timer
git commit -qam "move comps to one daily run at 12am"
