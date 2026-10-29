#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
cat > backfill.sh <<'SH'
#!/bin/bash
for i in $(seq 1 1200); do echo "row $i of 1200" >> backfill.log; sleep 1; done
SH
chmod +x backfill.sh
printf 'backfill.log\n' > .gitignore
git add -A && git commit -qm "add backfill"
