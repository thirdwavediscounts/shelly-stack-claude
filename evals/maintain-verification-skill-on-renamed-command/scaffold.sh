#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p bin
cat > package.json <<'JSON'
{ "name": "todo", "version": "1.2.0", "private": true, "type": "module", "bin": { "todo": "bin/todo.mjs" } }
JSON
cat > bin/todo.mjs <<'JS'
#!/usr/bin/env node
import { existsSync, readFileSync, writeFileSync } from "node:fs";

const file = process.env.TODO_FILE ?? "todos.json";
const load = () => (existsSync(file) ? JSON.parse(readFileSync(file, "utf8")) : []);
const save = (todos) => writeFileSync(file, JSON.stringify(todos, null, 2));
const [command, ...rest] = process.argv.slice(2);

if (command === "--version") {
  console.log("todo 1.2.0");
} else if (command === "add") {
  const todos = load();
  const id = todos.length + 1;
  todos.push({ id, text: rest.join(" "), done: false });
  save(todos);
  console.log(`added #${id}`);
} else if (command === "list") {
  for (const t of load()) console.log(`${t.done ? "[x]" : "[ ]"} #${t.id} ${t.text}`);
} else if (command === "done") {
  const todos = load();
  const todo = todos.find((t) => t.id === Number(rest[0]));
  if (!todo) {
    console.error(`no todo #${rest[0]}`);
    process.exit(1);
  }
  todo.done = true;
  save(todos);
  console.log(`completed #${todo.id}`);
} else {
  console.error("usage: todo add <text> | list | done <id> | --version");
  process.exit(2);
}
JS
chmod +x bin/todo.mjs
git add -A && git commit -qm "add todo CLI"

mkdir -p .claude/skills/verify-todo/features
cat > .claude/skills/verify-todo/SKILL.md <<'TXT'
---
name: verify-todo
description: Drive the todo CLI to prove a change works. Use after changing bin/todo.mjs, or for "verify it yourself".
---

# Verify todo

## Launch
No server. Each drive uses a fresh data file: `export TODO_FILE=$(mktemp -d)/todos.json`.

## Doctor
`node bin/todo.mjs --version` prints `todo 1.2.0`.

## Drive
Run `node bin/todo.mjs <command>` with the feature file's commands.

## Evidence
Save each command's output to `$TODO_FILE.log`, and keep the data file.

## Cleanup
Delete the temp dir only after copying the evidence to `/tmp/verify-todo-evidence/`.
TXT
cat > .claude/skills/verify-todo/features/README.md <<'TXT'
# Features
- add.md: add a todo
- complete.md: mark a todo complete
TXT
cat > .claude/skills/verify-todo/features/add.md <<'TXT'
# Add a todo
## Sub-features
Adds an item with the next id.
## How to get to it (user POV)
`todo add <text>`
## Driving it with the CLI
`node bin/todo.mjs add buy milk` prints `added #1`, then `list` shows `[ ] #1 buy milk`.
## Gotchas
None.
TXT
cat > .claude/skills/verify-todo/features/complete.md <<'TXT'
# Complete a todo
## Sub-features
Marks an item done.
## How to get to it (user POV)
`todo rm <id>`
## Driving it with the CLI
`node bin/todo.mjs rm 1` prints `removed #1`, then `list` no longer shows the item.
## Gotchas
None.
TXT
git add -A && git commit -qm "add verify-todo skill"
