#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p workflows/temu
cat > workflows/temu/token_check.py <<'PY'
import os
import time

import requests

PROXY = os.environ.get("DECODO_PROXY", "http://gate.decodo.com:7000")


def check_token(token: str) -> dict:
    for attempt in range(3):
        response = requests.post(
            "https://openapi.temu.com/api/token/check",
            json={"token": token},
            proxies={"https": PROXY},
            timeout=10,
        )
        if response.ok:
            return response.json()
        time.sleep(2 ** attempt)
    raise RuntimeError(f"Temu token check failed: {response.text}")
PY
git add -A && git commit -qm "add Temu token check"
sed -i.bak 's/range(3)/range(5)/' workflows/temu/token_check.py && rm workflows/temu/token_check.py.bak
git commit -qam "fix: retry the Temu token check more times"
sed -i.bak 's/timeout=10/timeout=30/' workflows/temu/token_check.py && rm workflows/temu/token_check.py.bak
git commit -qam "fix: give the Temu token check a longer timeout"
