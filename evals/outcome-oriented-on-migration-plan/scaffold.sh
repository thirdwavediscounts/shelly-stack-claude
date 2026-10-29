#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p workers deploy
cat > workers/comps_writer.py <<'PY'
import os

import psycopg

DB_URL = os.environ["LOCAL_SUPABASE_URL"]


def write(comps: list[dict]) -> None:
    with psycopg.connect(DB_URL) as conn:
        conn.executemany(
            "insert into ebay_auction_comps (item_id, price) values (%(item_id)s, %(price)s)",
            comps,
        )
PY
cat > deploy/com.twd.comps-writer.plist <<'XML'
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict>
  <key>Label</key><string>com.twd.comps-writer</string>
  <key>ProgramArguments</key><array><string>python3</string><string>workers/comps_writer.py</string></array>
  <key>StartInterval</key><integer>3600</integer>
</dict></plist>
XML
git add -A && git commit -qm "run the comps writer on the mac"
