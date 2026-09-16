---
name: arena
description: Spawn N parallel candidates at the same task, pick a base, graft the
  strongest parts of the losers into it. Use for $shelly-stack:arena, 'arena this',
  'throw it in the arena', or when one attempt at a non-trivial artifact would lock
  in the wrong shape.
---

> **Codex runtime:** Follow the [native runtime contract](../shelly-mode/references/codex-runtime.md) for model selection, subagents, planning, review, waits, and Codex paths.

# Arena

Fan out N parallel attempts at the same task. Read every candidate end to end. Pick the strongest as the base. Graft the best ideas from the others into it. Verify the synthesized result.

## Start

Start the native runtime contract's planning branch with one entry per phase before launching anything.

1. Frame
2. Fan out
3. Cross-judge
4. Pick
5. Graft
6. Verify

## Phase A: Frame

The N candidates will receive the same prompt, so the prompt is the contract.

1. State the artifact each candidate is producing.
2. Derive the rubric. State what success looks like for *this* task, then turn it into 3-6 concrete gradeable criteria. The rubric is the picker's tool in Phase D. Candidates only see the task.
3. Pick the runners. Use `arena runners` from `~/.codex/shelly-stack-models.md` when present. Otherwise choose the panel from the native runtime contract's dynamic fallback. Spawn more when the arena covers multiple design directions. Same model N times when the work is generation-bound rather than judgment-sensitive. A configured Codex role entry is `<model>@<reasoning_effort>`. Pass both values to `spawn_agent` with a non-`all` `fork_turns` when the current native schema supports them. For `inherit@inherit`, omit all three overrides. If a saved pair is unavailable, use the native runtime contract's dynamic fallback for that run and ask the user to rerun `$shelly-stack:setup-shelly-stack`.
4. Assign output paths. Before spawning a repository-writing candidate, the parent prepares a dedicated git worktree and passes its absolute path in that candidate's brief. For a non-repository artifact, prepare a distinct `/tmp/arena-<slug>/candidate-<n>/` directory. Passing only an output path inside a shared checkout is not isolation.

## Phase B: Fan out

Inspect current child capacity. Spawn up to the available child slots together, each with the task, shared grounding path, prepared worktree or output directory, and required rationale. When N exceeds capacity, refill a rolling window as candidates finish until all N have run.

Each rationale names the alternatives the candidate considered and what it rejected.

If a candidate fails to produce output, proceed with N-1 and note the dropout in the synthesis record.

## Phase C: Cross-judge

After all Phase B candidates complete, choose one `<model>@<reasoning_effort>` pair from `arena cross-judge pool` in `~/.codex/shelly-stack-models.md`, or use the native runtime fallback. Prefer a pair different from the parent's settings. Dispatch one judge with that pair through the native runtime contract's read-only worker branch. The judge sees the rubric and candidates by path label, scores each criterion, and recommends a base with rationale. Start it only after every candidate has finished so it cannot mistake partial output for a dropout.

## Phase D: Pick a base

Read every candidate end to end before picking.

Score each candidate against the rubric criterion by criterion, not on holistic feel. Compare against the cross-judge. Agreement on the base confirms the pick. Disagreement means one of you is biased or the rubric was ambiguous. Read both rationales before deciding.

Pick the base on which candidate a future maintainer can extend most easily without breaking invariants. Prefer the cleaner boundary or smaller API when two feel tied, per the Laziness Protocol.

Record the pick and the reason in a short synthesis note alongside the base artifact, including the cross-judge's verdict.

## Phase E: Graft

Walk each losing candidate once more and identify what is worth porting into the base. The signal is usually one or two things per candidate, not most of it.

Fold each graft in by hand, per the **redesign-from-first-principles** principle skill. Don't paste mechanically. The result has to remain coherent under one mental model.

Record what was grafted, from which candidate, and what was rejected and why.

When N candidates converge on the same shape, that is a strong agreement signal. Note the convergence in the record and ship the consensus shape. No graft is needed. When N candidates wildly diverge, Phase A was under-specified. Reframe and re-run rather than averaging the divergence.

## Phase F: Verify

The synthesized artifact has to hold up under the same scrutiny as any other output, per the **prove-it-works** principle skill.

If verification surfaces a problem the arena did not catch, either Phase A was wrong (re-frame and re-run) or one candidate caught it and you missed the graft (go back to Phase E). Don't paper over.

## Outputs

One synthesized artifact. One short synthesis note alongside, naming the base, the grafts (with source candidate), the rejections, the dropouts if any, and the verification result.
