#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
echo "# shop" > README.txt
git add -A && git commit -qm "init"
git tag v1.0.0
echo a >> README.txt && git commit -qam "feat: add CSV export"
echo b >> README.txt && git commit -qam "fix: cart total rounding"
