---
name: swarm
description: "Fan out N parallel workers, drain them, and return one report. Use for /swarm, 'swarm this', or parallel coverage, races, gauntlets, and exploration."
disable-model-invocation: true
---

# Swarm

Fan out N parallel local workers, each in its own worktree when it writes. They may cover separate slices, race the same brief, or mix both. The parent waits, aggregates, and returns one report.

## Start

Open a todolist with one entry per phase before launching anything.

1. Frame
2. Fan out
3. Aggregate
4. Report

## Phase A: Frame

1. State the done predicate and the artifact or report the swarm must return.
2. Choose the shape. Partition into slices, race N workers on identical briefs, or mix both. For a race or mixed shape, declare `first pass`, `rank all`, or `best-of` before spawning.
3. Set N from the user or derive it from the shape. N is total workers; size it for one machine.
4. Pick the worker model from `swarm workers` in `~/.claude/rules/shelly-stack-models.md` when present. Otherwise use `sonnet`. For a model race, name each arm's model up front. A configured role value is either an Agent `model` alias (`fable`, `opus`, `sonnet`, `haiku`) or the name of a user agent under `~/.claude/agents/` (shelly-agent's body with a pinned model and effort, named `shelly-<model>-<effort>`, for example `shelly-opus-high`). An alias goes in `model`. An agent name goes in `subagent_type` with `model` omitted; it already carries the shelly-agent body, so it replaces `shelly-stack:shelly-agent` and `general-purpose` for that spawn.
5. Give each worker its own writable output when it writes. Use a worktree, branch, or `/tmp/swarm-<slug>/worker-<n>/`.

## Phase B: Fan out

Invoking swarm is the user's opt-in to multi-agent orchestration, so run the fan-out with the `Workflow` tool, not N separate Agent calls. Load the `workflow-authoring` skill, then write one script: `parallel()` over the N briefs, each `agent(brief, opts)`. Set `opts.agentType` to the configured worker value when it is an agent name (for example `shelly-sonnet-medium`), or `opts.model` when it is a model alias. Set `opts.isolation: 'worktree'` for every worker that writes files, so each has one writer; omit it for read-only workers. Set `opts.schema` to the report shape below so each worker returns a validated object instead of prose. A worker that needs this session's checkout or something on the user's computer runs the same way; the Workflow runs locally.

When a worker must start from a non-default pushed branch, name that branch in its brief and tell it to check the branch out first.

Every brief stands alone. Include the goal, scope, exact slice or race arm, how to verify, and what to report. Reports use `PASS`, `ISSUES`, or `BLOCKED` with evidence.

If a worker drops out, proceed with N-1 and note it.

## Phase C: Aggregate

Read the terminal results. For coverage, every required slice needs a result. For a race, apply the selection rule declared up front. Use first pass, rank all, or best-of. Do not paste raw worker dumps.

Keep a compact result table, one-line evidenced issues, and explicit gaps or dropouts.

## Phase D: Report

Return one consolidated in-chat report with the table, issue one-liners, gaps or dropouts, and the race rule when used.
