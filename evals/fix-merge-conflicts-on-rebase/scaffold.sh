#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src
printf 'export const BATCH_SIZE = 100;\nexport const WORKERS = 4;\n' > src/config.mjs
git add -A && git commit -qm "add config"
git checkout -q -b sean/bigger-batch
printf 'export const BATCH_SIZE = 500;\nexport const WORKERS = 4;\n' > src/config.mjs
git commit -qam "raise the batch size to 500"
git checkout -q main
printf 'export const BATCH_SIZE = 200;\nexport const WORKERS = 8;\n' > src/config.mjs
git commit -qam "raise the batch size to 200 and workers to 8"
git checkout -q sean/bigger-batch
