#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src .github/workflows
cat > .env.example <<'TXT'
EBAY_CLIENT_ID=
EBAY_CLIENT_SECRET=
TXT
cat > src/ebay.mjs <<'JS'
export const ebayConfig = () => ({ clientId: process.env.EBAY_CLIENT_ID, clientSecret: process.env.EBAY_CLIENT_SECRET });
JS
cat > .github/workflows/ci.yml <<'YML'
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: node --test
        env:
          EBAY_CLIENT_SECRET: ${{ secrets.EBAY_CLIENT_SECRET }}
YML
echo ".env.local" > .gitignore
git add -A && git commit -qm "add eBay client"
