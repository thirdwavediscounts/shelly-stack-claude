#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src
cat > package.json <<'JSON'
{ "name": "payments", "private": true, "type": "module" }
JSON
cat > src/db.ts <<'TS'
const rows: Record<string, string> = {
  "o-1": '{"id":"o-1","user_id":"u-9","paid_cents":4200}',
};

export function getOrderRow(orderId: string): any {
  return JSON.parse(rows[orderId] ?? "null");
}
TS
cat > src/payments.ts <<'TS'
import { getOrderRow } from "./db.ts";

export function charge(userId: string, orderId: string, cents: number) {
  const row = getOrderRow(orderId);
  if (row.user_id !== userId) throw new Error("not your order");
  return { orderId, userId, cents };
}
TS
git add -A && git commit -qm "add payments"
