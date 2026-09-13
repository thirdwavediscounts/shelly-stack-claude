# Swarm

Fan out N parallel local workers, each in its own worktree when it writes. They may cover separate slices, race the same brief, or mix both. The parent waits, aggregates, and returns one report.

## Start

Start the native runtime contract's planning branch with one entry per phase before launching anything.

1. Frame
2. Fan out
3. Aggregate
4. Report

## Phase A: Frame

1. State the done predicate and the artifact or report the swarm must return.
2. Choose the shape. Partition into slices, race N workers on identical briefs, or mix both. For a race or mixed shape, declare `first pass`, `rank all`, or `best-of` before spawning.
3. Set N from the user or derive it from the shape. N is total workers; size it for one machine.
4. Pick the worker `<model>@<reasoning_effort>` pair from `swarm workers` in `~/.codex/shelly-stack-models.md`, or use the native runtime fallback. For a model race, name each arm's full pair before spawning. A configured Codex role entry is `<model>@<reasoning_effort>`. Pass both values to `spawn_agent` with a non-`all` `fork_turns` when the current native schema supports them. For `inherit@inherit`, omit all three overrides. If a saved pair is unavailable, use the native runtime contract's dynamic fallback for that run and ask the user to rerun `$shelly-stack:setup-shelly-stack`.
5. Give each writing worker a dedicated git worktree that the parent prepares before spawning, or a distinct `/tmp/swarm-<slug>/worker-<n>/` path for non-repository artifacts. A branch name alone is not isolation because native collaboration subagents can share a checkout.

## Phase B: Fan out

Invoking swarm is the user's opt-in to multi-agent orchestration. Inspect current child capacity, spawn up to the available slots together with native `spawn_agent` calls, and refill a rolling window until all N workers have run. Give each one a concrete brief with the configured model and `reasoning_effort`. Give writers non-overlapping ownership or a dedicated git worktree, require the report shape below, and collect them with `wait_agent`.

When a worker must start from a non-default pushed branch, the parent prepares a dedicated worktree at that branch before spawning and passes its path in the brief. Never ask parallel workers to check out branches in a shared checkout.

Every brief stands alone. Include the goal, scope, exact slice or race arm, how to verify, and what to report. Reports use `PASS`, `ISSUES`, or `BLOCKED` with evidence.

If a worker drops out, proceed with N-1 and note it.

## Phase C: Aggregate

Read the terminal results. For coverage, every required slice needs a result. For a race, apply the selection rule declared up front. Use first pass, rank all, or best-of. Do not paste raw worker dumps.

Keep a compact result table, one-line evidenced issues, and explicit gaps or dropouts.

## Phase D: Report

Return one consolidated in-chat report with the table, issue one-liners, gaps or dropouts, and the race rule when used.
