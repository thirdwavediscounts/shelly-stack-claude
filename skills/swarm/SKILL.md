---
name: swarm
description: "Fan out N parallel workers, drain them, and return one report. Use for /swarm, 'swarm this', or parallel coverage, races, gauntlets, and exploration."
disable-model-invocation: true
---

# Swarm

Fan out N parallel cloud workers. They may cover separate slices, race the same brief, or mix both. The parent waits, aggregates, and returns one report.

## Start

Open a todolist with one entry per phase before launching anything.

1. Frame
2. Fan out
3. Aggregate
4. Report

## Phase A: Frame

1. State the done predicate and the artifact or report the swarm must return.
2. Choose the shape. Partition into slices, race N workers on identical briefs, or mix both. For a race or mixed shape, declare `first pass`, `rank all`, or `best-of` before spawning.
3. Set N from the user or derive it from the shape. N is total workers, not the cloud concurrency limit.
4. Pick the worker model from `swarm workers` in `~/.claude/rules/shelly-stack-models.md` when present. Otherwise use `sonnet`. For a model race, name each arm's model up front. A configured role value is either an Agent `model` alias (`fable`, `opus`, `sonnet`, `haiku`) or the name of a user agent under `~/.claude/agents/` (shelly-agent's body with a pinned model and effort, named `shelly-<model>-<effort>`, for example `shelly-opus-high`). An alias goes in `model`. An agent name goes in `subagent_type` with `model` omitted; it already carries the shelly-agent body, so it replaces `shelly-stack:shelly-agent` and `general-purpose` for that spawn.
5. Give each worker its own writable output when it writes. Use a worktree, branch, or `/tmp/swarm-<slug>/worker-<n>/`.

## Phase B: Fan out

Spawn all N workers in one message with the configured worker value (`subagent_type: "general-purpose"` plus `model`, or the agent name as `subagent_type`) and `isolation: "remote"`. Remote isolation is availability-gated: when it is off, the harness silently runs the worker in a local git worktree under `.claude/worktrees/` on this machine, which still gives one writer per worktree. Omit `isolation` only when the worker needs this session's checkout or something on the user's computer. When the user has opted into multi-agent orchestration (they asked to fan out agents or run a workflow), the `Workflow` tool can run the same fan-out as one deterministic script instead of N Agent calls.

When a worker must start from a non-default pushed branch, name that branch in its brief and tell it to check the branch out first.

Every brief stands alone. Include the goal, scope, exact slice or race arm, how to verify, and what to report. Reports use `PASS`, `ISSUES`, or `BLOCKED` with evidence.

If a worker drops out, proceed with N-1 and note it.

## Phase C: Aggregate

Read the terminal results. For coverage, every required slice needs a result. For a race, apply the selection rule declared up front. Use first pass, rank all, or best-of. Do not paste raw worker dumps.

Keep a compact result table, one-line evidenced issues, and explicit gaps or dropouts.

## Phase D: Report

Return one consolidated in-chat report with the table, issue one-liners, gaps or dropouts, and the race rule when used.
