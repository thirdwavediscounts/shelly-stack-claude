---
name: untangle-codebase
description: "Untangle one app or package so later changes land in one place. Lists every hidden link, needless link, surplus piece, and special case, redesigns from first principles, fixes all of it against a pinned behavior baseline, and repeats until nothing worth fixing is left. Runs only when the user types /untangle-codebase."
argument-hint: "[app, package, or folder to untangle]"
---

# Untangle codebase

Refactor one unit of code until a typical change lands in one place. Every piece of code gets the same question. **Should these pieces change together?** Behavior stays the same, apart from bugs the redesign fixes on the way. This is the **Refactoring** playbook at full scale (`../shelly-mode/playbooks/refactoring.md`), so its rules apply here too.

The target is `$ARGUMENTS`. With no target, list the units, pick the one with the most commits in the last 90 days, say which one you picked, and start.

## 1. Frame

1. Split the target into units. A unit is one app or one package. A shared package is its own unit, because a change there reaches every app that imports it. One run untangles one unit and ships one PR.
2. List what must not change before you look for problems. Read the repo's CLAUDE.md files, rules, and memory. Out of scope:
   - Anything another system depends on. Public routes, env var names, service and cron IDs, OAuth origins, exported package APIs, database schema, and RPCs.
   - Code another person owns.
   - Copies the repo's rules say are on purpose.

   A fix that needs one of these goes to the open items for the user. It never goes into the diff.
3. Pin behavior, per step 1 of the Refactoring playbook. Capture how the unit behaves now with the project's verify skill, its end-to-end tests, or a recorded baseline. Type check and lint are not a pin. Without a pin, stop and build one first.
4. Count the unit's source lines and start a decision log with the **show-me-your-work** skill.

## 2. List every problem

Change nothing yet. Go through the unit and write down every place where the code answers the question wrong. Write each as `file:line` and one plain sentence in `problems.md` beside the decision log. There are three ways to get it wrong.

**Hidden links.** Pieces that must change together, where the code does not show it.

- Copies of logic or values. Change one and the others must change too, but nothing says so.
- A module that reads a global or a file another module sets.
- One feature split across folders by layer, so one change touches all of them.
- A call order or convention callers just have to know.

**Needless links.** Pieces tied together that change for different reasons.

- Callers that depend on another module's internals.
- Stable code that imports something more volatile.
- A general function with a parameter only one workflow understands.
- A shallow module, whose interface changes whenever its internals do.

**Surplus.** Pieces with no reason of their own to change.

- Wrappers that only pass calls through.
- Extension points and config for things that never vary.
- Dead code.

Also write down every **special case**. Look for an `if` for one value, a parameter for one caller, a swallowed exception, a retry or sleep, and a disabled test. Each one is a requirement the design never accounted for. Use them to work out what the system needs to be.

Use git as evidence. Files that keep changing in the same commits but live apart are hidden links.

## 3. Redesign

Read `../principle-redesign-from-first-principles/SKILL.md` and `../principle-model-the-domain/SKILL.md`.

1. Work out each fix as if the system had known today's requirements from the start. Look for the one fix behind several problems. It often looks nothing like them. Do not fix special cases one at a time.
2. Check every fix the same way. Pieces that change together end up together. Pieces that don't are not tied. Everything depends on what changes less.
3. A fix that adds or changes a type, an exported signature, or a module boundary runs the **architect** skill first.
4. Rewrite `problems.md` with each fix written above the problems it solves, as in the example below.

## 4. Fix

1. Subtract first. Delete dead code, pass-through wrappers, and config that never varies (`../principle-subtract-before-you-add/SKILL.md`).
2. Land one fix per commit. After each commit, rerun the pin. If behavior changed, revert the commit and log why.
3. Remove the special cases the redesign makes unnecessary. Keep the ones the system still needs.
4. Delegate mechanical edits as step 5 of the Refactoring playbook says.
5. Change tests last, since they are the safety net. Remove tests that cannot fail or that repeat the implementation. Rewrite tests tied to internals so they check behavior (`../principle-test-behavior-not-implementation/SKILL.md`). The **no-comments** skill handles comments when Opening a PR runs it.

## 5. Check and repeat

Run the **swarm** skill with four read-only workers over the unit, one each for hidden links, needless links, surplus, and special cases. Each returns `file:line` findings. Take what they find back to step 2. Stop when a round finds nothing worth fixing.

The unit is done when:

- Few special cases are left. How many remain is the best measure of how close you are.
- A typical change lands in one place.
- Every import is reasonable, and nothing imports something more volatile than itself.
- The pin passes with the same behavior as at the start.

Then run **Opening a PR**.

## Tips

- Strip the function bodies with a script, so the whole unit's skeleton fits in context.
- Have subagents summarize parts of the unit, so you can reason across all of it at once.
- Script a graph of what imports what, and rerun it after each fix.
- Start where one fix would clear the most problems.

## Example `problems.md`

The list:

```md
- `ui/LogoutDialog.tsx:30` waits 100ms after closing and hopes the message input can take focus by then.
- `ui/SettingsDialog.tsx:61` sets a global `skipRefocus` flag to stop the logout dialog from focusing the message input.
- `checkout/submit.ts:9` depends directly on `payments/stripe.ts`.
- `refunds/refund.ts:22` wraps every Stripe call in `if (order.provider === "paypal")`.
```

After the redesign:

```md
- Make the general `Dialog` give focus back to whatever had it before it opened, so the wait and the flag can both go.
  - `ui/LogoutDialog.tsx:30` waits 100ms after closing and hopes the message input can take focus by then.
  - `ui/SettingsDialog.tsx:61` sets a global `skipRefocus` flag to stop the logout dialog from focusing the message input.
- Define a `PaymentProvider` interface that Stripe and PayPal both implement, so checkout and refunds stop knowing which one they use.
  - `checkout/submit.ts:9` depends directly on `payments/stripe.ts`.
  - `refunds/refund.ts:22` wraps every Stripe call in `if (order.provider === "paypal")`.
```

## Reply

- The unit and its PR.
- Each fix that shipped, with the problems it cleared.
- The pin, and its result before and after.
- Special cases and source lines in the unit, before and after.
- Open items: fixes the out-of-scope list blocked.
- The next unit to untangle.
