---
name: typescript-conventions
description: Apply Shelly Team Kit import placement and exhaustive-switch conventions
  when reading or editing TypeScript files.
---

# TypeScript conventions

Read the [runtime contract](../../references/runtime.md) and follow the repository's TypeScript rules.

Use a `never` exhaustiveness check when switching over discriminated unions or enums so a new variant fails compilation until handled.

Keep static imports at module scope. Prefer a top-level `import type` over an inline import type. Retain dynamic imports when they implement lazy loading or resolve a demonstrated dependency cycle. Do not convert them mechanically.
