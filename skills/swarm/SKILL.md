---
name: swarm
description: "Fan out N parallel workers, drain them, and return one report. Use for /swarm, 'swarm this', or when a shelly-mode playbook or another skill calls for parallel coverage, races, gauntlets, or exploration."
---

# Swarm

## Start

Open a todolist with one entry per phase before launching anything.

1. Frame
2. Fan out
3. Aggregate
4. Report

## Phase A: Frame

1. State the done predicate and the artifact or report the swarm must return.
2. Choose the shape. Partition into slices, race N workers on identical briefs, or mix both. For a race or mixed shape, declare `first pass`, `rank all`, or `best-of` before spawning.
3. Set N from the user or derive it from the shape. N is total workers; size it for one machine. State the spawn ceiling, the total workers across every refill, up front.
4. Pick the worker model from the `swarm workers` line in `~/.claude/rules/shelly-stack-models.md`. If the rule or that line is missing, use `sonnet`. For `inherit`, leave the model unset so the workers run on the parent model. If a configured value is rejected, use `sonnet` and say so. For a model race, name each arm's model up front. A configured value is an Agent `model` alias (`fable`, `opus`, `sonnet`, `haiku`) or a pinned agent name such as `shelly-stack:shelly-sonnet-medium`, per the Subagents section of the **shelly-mode** skill (Read `../shelly-mode/SKILL.md`).
5. Give each worker its own writable output when it writes. When workers verify or measure commits, each brief names the exact SHAs. A measurement brief also names the method (sample count, what one sample is, order). The worker records both in its result.

## Phase B: Fan out

Invoking swarm is the user's opt-in to multi-agent orchestration, so run the fan-out with the `Workflow` tool, not N separate Agent calls. Load the `workflow-authoring` skill, then write one script: `parallel()` over the N briefs, each `agent(brief, opts)`. Set `opts.agentType` to the configured worker value when it is an agent name (for example `shelly-stack:shelly-sonnet-medium`), or `opts.model` when it is a model alias, and neither for `inherit`. Set `opts.isolation: 'worktree'` for every worker that writes files, so each has one writer; omit it for read-only workers. Set `opts.schema` to the report shape below so each worker returns a validated object instead of prose. A worker that needs this session's checkout or something on the user's computer runs the same way; the Workflow runs locally.

When a worker must start from a non-default pushed branch, name that branch in its brief and tell it to check the branch out first.

Every brief stands alone. Include the goal, scope, exact slice or race arm, how to verify, and what to report. Reports use `PASS`, `ISSUES`, or `BLOCKED` with evidence. A worker that can prove a defect reports `ISSUES` and lists every issue it can prove, not only the first. Every worker carries the explicit model or agent name from Phase A step 4; none spawns on the default. No worker runs a repo-wide formatter such as `prettier --write .`; each formats only its own files, or the parent formats once after Phase C.

If a worker drops out, proceed with N-1 and note it. Before each refill wave, check remaining usage and stop spawning once the ceiling from Phase A is reached, reporting the slices left uncovered.

## Phase C: Aggregate

Read the terminal results. Drop a result that does not record the SHAs and method its brief names, and respawn that worker once. After a second miss, record a gap. A gap does not count as a pass. For coverage, every required slice needs a result. For a race, apply the selection rule declared up front. Use first pass, rank all, or best-of. Do not paste raw worker dumps.

## Phase D: Report

Return one consolidated in-chat report with a result table, issue one-liners, gaps or dropouts, and the race rule when used.
