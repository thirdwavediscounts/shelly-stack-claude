#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src test
cat > package.json <<'JSON'
{ "name": "discount", "private": true, "type": "module", "scripts": { "test": "node --test" } }
JSON
cat > src/discount.mjs <<'JS'
export const RATES = { SAVE10: 0.1, SAVE25: 0.25 };

export const helpers = {
  lookupRate(code) {
    return RATES[code] ?? 0;
  },
};

export function applyDiscount(total, code) {
  const rate = helpers.lookupRate(code);
  return Math.round(total * (1 - rate) * 100) / 100;
}
JS
cat > test/discount.test.mjs <<'JS'
import { test, mock } from "node:test";
import assert from "node:assert/strict";
import { applyDiscount, helpers } from "../src/discount.mjs";

test("looks up the rate", () => {
  const spy = mock.method(helpers, "lookupRate");
  applyDiscount(100, "SAVE10");
  assert.equal(spy.mock.callCount(), 1);
});
JS
git add -A && git commit -qm "add applyDiscount"
