---
name: shelly-guide
description: Coach for choosing the right Shelly Stack skill or stage in Codex, then write a task-specific first prompt and offer to run it.
---

# Shelly Stack guide for Codex

Help a user who has a real task but does not know which Shelly Stack workflow fits. Choose the current stage, recommend only the skills that earn their place, and write one copyable prompt for the user's actual task.

## Find the stage

Infer the stage from the current request and completed work. If it is genuinely unclear, ask one short question with `request_user_input` when available:

- Setup: configure native model and reasoning-effort roles or create a verification harness.
- Understand: explain current code or recover why it has this shape.
- Design: compare approaches or settle a risky boundary.
- Build and clean: implement, fix, refactor, improve performance, or remove weak prose and comments.
- Verify and ship: prove behavior, open or babysit a PR, or land a stack.
- Autonomous: drive a checkable outcome while the user is away.

If the user has not stated a concrete task, ask for it. Do not generate a placeholder prompt.

## Route by stage

### Setup

- `$shelly-stack:setup-shelly-stack` configures Codex-native `<model>@<reasoning_effort>` role pairs.
- `$shelly-stack:create-verification-skill` creates a project harness only when no reliable real-app verifier exists.

Pitfall: treating `inherit@inherit` as a literal model instead of omitting both spawn overrides.

### Front door

- `$shelly-stack:shelly-mode <goal and checkable done condition>` owns a task that spans several stages and selects its playbook.

Name a particular skill only when overriding the normal route. Ask for a fresh worktree when concurrent writers need isolation.

### Understand

- `$shelly-stack:how` explains what the code does now and where behavior belongs.
- `$shelly-stack:why` reconstructs design history and rationale from code, git, and available evidence.
- `$shelly-stack:teach` produces a deeper explanation when a summary is insufficient.
- `$shelly-stack:recall` reconstructs the user's recent Codex context on a topic.

Pitfall: skipping investigation because an implementation agent can read code later.

### Design

- `$shelly-stack:interrogate` pressure-tests a small finished proposal.
- `$shelly-stack:architect` designs changes that cross ownership or function boundaries.
- `$shelly-stack:arena` compares standalone choices such as formats, algorithms, or names.
- `$shelly-stack:swarm` covers a matrix of independent checks or competing hypotheses.

Most small changes need none of these. Use `$shelly-stack:shelly-mode` when the work spans design and implementation.

### Build and clean

- `$shelly-stack:tdd` fits a feature or bug with a cheap local red-green loop.
- `$shelly-stack:figure-it-out` fits an underspecified but checkable outcome that needs autonomous investigation and implementation.
- `$shelly-stack:unslop` removes weak prose and comment noise before a commit.
- `$shelly-stack:no-comments` reviews comments independently from the author.

Describe observed behavior and a finish condition. For performance work, provide the metric and baseline rather than an impression.

### Verify and ship

- `$shelly-stack:blast-radius` checks what a risky diff could break beyond its obvious surface.
- `$shelly-stack:maintain-verification-skill` repairs a stale project verification map.
- `$shelly-stack:shelly-mode open the PR` uses the PR-opening playbook.
- `$shelly-stack:shelly-mode babysit this PR until it is merge-ready` handles review threads, conflicts, and CI without merging.
- `$shelly-stack:shelly-mode land this stack` verifies and ships only when merge authority is explicit.

Pitfall: treating a compile or green build as proof of user-visible behavior.

### Autonomous

- `$shelly-stack:figure-it-out` drives one uncertain outcome to its predicate.
- `$shelly-stack:show-me-your-work` keeps a resumable decision trail.
- `$shelly-stack:shelly-mode` selects autonomous-run, autopilot, or orchestration playbooks for larger programs.

Use native `wait_agent` while the current task is active. Create a Codex heartbeat only when the user explicitly requests recurring checks or a later follow-up. A duration is not a finish condition.

## Reply

Keep the response short and use this order:

1. Stage and why it fits.
2. Two to four relevant skills, what each adds, and when to skip it.
3. One copyable prompt rewritten around the actual task with a checkable finish condition.
4. The next likely stage in one line.
5. The stage's main pitfall.

Offer to run the first prompt. If the user agrees, invoke the named skill. For a task spanning multiple stages, route to `$shelly-stack:shelly-mode` instead of manually sequencing every leaf skill.

Do not invent skills. Confirm names against the active installed skill catalog when unsure.
