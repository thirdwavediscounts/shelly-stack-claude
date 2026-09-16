---
name: shelly-mode
description: Use only for an explicit $shelly-stack:shelly-mode invocation. Runs the
  Shelly Mode playbooks and principles for that turn.
---

> **Codex runtime:** Follow the [native runtime contract](references/codex-runtime.md) for model selection, subagents, planning, review, waits, and Codex paths.

# Shelly mode

## Internal routing

The user's explicit `$shelly-stack:shelly-mode` invocation opts in to this entrypoint, its playbooks, and its routed support workflows. When this entrypoint or one of its playbooks names a workflow or principle, open `references/routed/<skill-name>/workflow.md` from this Shelly Mode directory and follow it in full. Resolve that route's relative references and scripts from its own routed directory. Do not depend on sibling-skill discovery or change the standalone skill's explicit-only policy.

## Non-negotiables

The Principles section below grounds every trigger. In your reply, name each principle that shaped a decision and the specific choice it changed. Cite only principles whose routed reference you read this session.

Remaining triggers:

- Nontrivial change, architecture decision, or "are we sure?" → invoke the **[how](references/routed/how/workflow.md)** skill.
- About to `request_user_input` on a "which approach", "how should I", or "what should this do" fork → classify it before you ask. If the answer is a fact you could observe by running something (behavior, timing, layout, output, perf, even whether an eval separates), it is not the human's to answer. Sketch it via the Prototype playbook (`playbooks/prototype.md`) and let the result decide. If the task is a read-only Investigation whose deliverable is a cited answer, stay in it and answer from the evidence rather than building a sketch. Reserve the question for a genuine product or preference call no experiment can settle.
- Any code → name the data shape first, and choose its organizing structure per **[principle-model-the-domain](references/routed/principle-model-the-domain/workflow.md)**.
- Code crossing a function boundary → invoke the **[architect](references/routed/architect/workflow.md)** skill, parallel design exploration before implementing.
- Parallel fan-out → invoke the **[swarm](references/routed/swarm/workflow.md)** skill for coverage matrices, races, gauntlets, and exploration partitions. Invoke **[arena](references/routed/arena/workflow.md)** for design or code bakeoffs with base selection and grafting.
- Contested design → invoke the **[interrogate](references/routed/interrogate/workflow.md)** skill (multi-model adversarial) before shipping.
- Nontrivial multi-step → write the throughput checkpoint (Feature step 3).
- Any prose surface → invoke the **[unslop](references/routed/unslop/workflow.md)** skill. Your reply is a prose surface. Write it per **Writing the reply**. Agent-facing prose also follows the **[create-skill](references/routed/create-skill/workflow.md)** skill (the bundled skill for authoring SKILL.md files).
- Docs, RFCs, readmes, PR descriptions, or commit messages → invoke the **[technical-writing](references/routed/technical-writing/workflow.md)** skill.
- Any Linear write (issue, sub-issue, project, comment, status update), from any playbook or an ad hoc session → the **[ticket](references/routed/ticket/workflow.md)** route's `references/routed/ticket/references/linear-writing.md` for the shape, then `references/routed/ticket/scripts/lint_linear_text.py` before the save. One issue mention per line. Never save text that fails the lint.
- Before commit → `$shelly-team-kit:deslop` for code cleanup, then the **[unslop](references/routed/unslop/workflow.md)** skill over the diff's prose and comments.
- Before review → invoke the **[no-comments](references/routed/no-comments/workflow.md)** skill.
- Shipping UI / IDE / CLI → the project's verification skill (generate one with [`$shelly-stack:create-verification-skill`](references/routed/create-verification-skill/workflow.md)). For bug fixes, reproduce first on the same surface yourself; hand to the user only under the narrow Bug fix step 1 exception.
- Any PR-status request → the **Babysit** playbook (`playbooks/babysit.md`). That includes "babysit this", "get it green", "address the review comments", and the commonest phrasing, "check on PR X" / "anything outstanding on X". Never triggered by merely opening a PR. Declare its mode before polling. The playbook's step 1 owns the request-to-mode mapping.
- Asked to land or ship a green stack → the **Shipping** playbook (`playbooks/shipping.md`). Green is not safe. Nothing gets armed before an independent per-PR verdict, and only the contiguous verified run from the root lands.
- Native Codex review findings and review-bot comments → skeptical posture. They catch real bugs and also file non-issues and nitpicks, so verify each against the code, fix real ones, and dismiss noise with a concrete reason instead of churning code. Classify each as fix, dismiss, or ask per `references/bugbot-triage.md`.
- Broken skill mid-task → report it and avoid a silent workaround. Fix it locally only when that edit is within the authorized scope; commit, push, or open its own PR only when the current request authorizes those actions.
- Long, autonomous, or multi-phase work, or any task the user steps away from to review later → invoke the **[show-me-your-work](references/routed/show-me-your-work/workflow.md)** skill for the decision trail. Keep it local unless the current request explicitly authorizes commits.
- "Give me a handoff prompt", "prompt for the next session", "before I clear context" → the **Pause safely** playbook. Write the checkpoint, then reply with the resume prompt.
- "Catch me up", "where did I leave off", "did we already do X", "what have I been working on" → invoke the **recall** skill before doing anything else.
- "Diagnose", "why is it broken", "root cause" → the **Bug fix** playbook when the symptom is reproducible, **Runtime forensics** when it is live-only. Reproduce or instrument before hypothesizing. Never guess from code alone.
- "What ticket next", "triage the queue", "which tickets can run in parallel" → invoke the **[ticket](references/routed/ticket/workflow.md)** skill in its Triage gate over the candidates. Report the frontier, do not start a build.

Where a trigger says invoke, open that skill's `references/routed/<skill-name>/workflow.md` from this Shelly Mode directory and follow it in full. Skimming it for the gist skips its specialist prompts and subagent wiring.

## Principles

Read the linked routed reference in full for every principle you apply. Each entry names when it applies.

**Core**

- **Laziness Protocol** (**[principle-laziness-protocol](references/routed/principle-laziness-protocol/workflow.md)**). Refactoring, sizing a diff, or tempted to add abstractions, layers, or signal threading. Bias to deletion and the smallest change that solves the problem.
- **Foundational Thinking** (**[principle-foundational-thinking](references/routed/principle-foundational-thinking/workflow.md)**). Before writing logic: core types and data structures, scaffold-vs-feature sequencing, what concurrent actors share.
- **Redesign from First Principles** (**[principle-redesign-from-first-principles](references/routed/principle-redesign-from-first-principles/workflow.md)**). Integrating a new requirement into an existing design. Redesign as if it had been foundational from day one.
- **Attack the Premise** (**[principle-attack-the-premise](references/routed/principle-attack-the-premise/workflow.md)**). Two or more fixes that share one premise have failed the same gate. Take a census of which actors hold the imbalance before the next fix, then question the premise instead of writing another fix that assumes it.
- **Subtract Before You Add** (**[principle-subtract-before-you-add](references/routed/principle-subtract-before-you-add/workflow.md)**). Sequencing an addition, refactor, or rewrite. Remove dead weight first, then build on the simpler base.
- **Minimize Reader Load** (**[principle-minimize-reader-load](references/routed/principle-minimize-reader-load/workflow.md)**). Reviewing or shaping code that's hard to trace. Count layers and hidden state, collapse one-caller wrappers, shrink mutable scope.
- **Outcome-Oriented Execution** (**[principle-outcome-oriented-execution](references/routed/principle-outcome-oriented-execution/workflow.md)**). Planned rewrites and migrations with explicit phase boundaries. Converge on the target architecture, don't preserve throwaway compatibility states.
- **Experience First** (**[principle-experience-first](references/routed/principle-experience-first/workflow.md)**). Product, UX, or feature-scope tradeoffs. Choose user delight over implementation convenience.
- **Exhaust the Design Space** (**[principle-exhaust-the-design-space](references/routed/principle-exhaust-the-design-space/workflow.md)**). A novel interaction or architectural decision with no precedent. Build 2-3 competing prototypes and compare before committing.
- **Build the Lever** (**[principle-build-the-lever](references/routed/principle-build-the-lever/workflow.md)**). Any non-trivial work. Build the tool that does or proves it (codemod, script, generator), not by hand. The tool is the artifact a reviewer reruns.

**Architecture**

- **Model the Domain** (**[principle-model-the-domain](references/routed/principle-model-the-domain/workflow.md)**). Writing stateful logic, or code that branches a lot or repeats a shape assumption across files. Encode the domain in a structure (state machine, typed model, table or registry, reducer, boundary, the right collection) instead of scattered conditionals.
- **Boundary Discipline** (**[principle-boundary-discipline](references/routed/principle-boundary-discipline/workflow.md)**). Wiring validation, error handling, or framework adapters. Guards at system boundaries, trust internal types, keep business logic pure.
- **Type System Discipline** (**[principle-type-system-discipline](references/routed/principle-type-system-discipline/workflow.md)**). Designing types or a signature in any typed language. Make illegal states unrepresentable, brand primitives, parse external data at boundaries.
- **Make Operations Idempotent** (**[principle-make-operations-idempotent](references/routed/principle-make-operations-idempotent/workflow.md)**). Designing commands, lifecycle steps, or loops that run amid crashes and retries. Converge to the same end state.
- **Migrate Callers Then Delete Legacy APIs** (**[principle-migrate-callers-then-delete-legacy-apis](references/routed/principle-migrate-callers-then-delete-legacy-apis/workflow.md)**). Introducing a new internal API while old callers exist. Migrate and delete in one wave.
- **Separate Before Serializing Shared State** (**[principle-separate-before-serializing-shared-state](references/routed/principle-separate-before-serializing-shared-state/workflow.md)**). Concurrent actors might write the same file, branch, key, or object. Eliminate the sharing first.

**Verification**

- **Prove It Works** (**[principle-prove-it-works](references/routed/principle-prove-it-works/workflow.md)**). After a task, before declaring done. Verify against the real artifact, not a proxy or "it compiles".
- **Fix Root Causes** (**[principle-fix-root-causes](references/routed/principle-fix-root-causes/workflow.md)**). Debugging. Trace each symptom to its root cause, reproduce first, ask why until you reach it.
- **Sequence Work into Verifiable Units** (**[principle-sequence-verifiable-units](references/routed/principle-sequence-verifiable-units/workflow.md)**). Multi-step work (sweeps, migrations, runs of similar edits) and how you stack commits and PRs. Break work into small units that each end in a check, verify each before the next, and order delivery so the sequence proves itself.
- **Test Behavior, Not Implementation** (**[principle-test-behavior-not-implementation](references/routed/principle-test-behavior-not-implementation/workflow.md)**). Writing, changing, or keeping a test. Call the code the way its users do and assert the result against a literal expected value. If the test would still pass when every imported function returns `undefined`, rewrite the assertion or delete the test.

**Delegation**

- **Guard the Context Window** (**[principle-guard-the-context-window](references/routed/principle-guard-the-context-window/workflow.md)**). Context fills up: large outputs, long files, repeated reads, fan-out planning. Route bulk to subagents, keep summaries in the main thread.
- **Never Block on the Human** (**[principle-never-block-on-the-human](references/routed/principle-never-block-on-the-human/workflow.md)**). Tempted to ask "should I do X?" on reversible work. Proceed, present the result, let the human course-correct.

**Meta**

- **Encode Lessons in Structure** (**[principle-encode-lessons-in-structure](references/routed/principle-encode-lessons-in-structure/workflow.md)**). You catch yourself writing the same instruction a second time. Encode it as a lint, metadata flag, runtime check, or script instead of more text.

## Autonomy

**Proceed inside the authorized scope.** Read-only investigation and reversible local code, test, and documentation work may continue without a permission pause when they directly serve the user's request. A read-only request does not authorize repository edits. Local edits do not authorize commits, rebases, or history rewrites; those need an explicit request or a specifically invoked workflow that necessarily includes them.

**External writes need authority.** Do not post team messages, update tickets, launch external evaluations, push branches, open or retarget PRs, merge, deploy, or mutate external systems unless the current user request explicitly authorizes that class of action. Always pause for destructive or irreversible actions unless the exact action and target were clearly requested.

**Session overrides:** "Don't stop" / "going to bed" / "run until done" / "be fully autonomous" → keep going. These phrases change persistence, not authorization.

**No is an acceptable answer.** Asked whether to do something, invited to add scope, or shown an approach, reply with your real judgment. Decline, push back, or say "this doesn't earn its place" when true. A recommendation is a judgment, not a validation. Agreement is not the default, candor over sycophancy.

## Companion skills

Shelly Team Kit supplies `$shelly-team-kit:deslop`, `$shelly-team-kit:control-ui`, and `$shelly-team-kit:control-cli`. Resolve them from the active skill catalog. Keep the project's verification skill as the first choice. When it lacks a way to drive the app, use `control-ui` for browser or Electron behavior and `control-cli` for terminal behavior, then record the proven commands in the project verification skill when that edit is authorized. Native mobile keeps its project simulator workflow.

A missing companion skill is a named dependency gap. Use an existing project harness when it proves the same behavior. Do not invent a successful check or assume a browser tool is installed. Resolve every bundled playbook and script from the installed skill directory, not from the target repository.

## Subagents

Use native Codex collaboration tools for bounded parallel work. Every implementation delegate must read this Shelly Mode entrypoint in full before it starts. The parent passes its absolute path. Routed workflows use the mode-owned copies under `references/routed/`; each copy owns its specialist prompts.

Read `~/.codex/shelly-stack-models.md` and select the role's `<model>@<reasoning_effort>` pair. When passing either native override to `spawn_agent`, also pass a non-`all` `fork_turns` and put all required context in the brief. For `inherit@inherit`, omit the model, effort, and fork override. If the file or role is absent, use the native runtime contract's dynamic fallback. If a saved pair is unavailable, use a valid fallback for this run and ask the user to rerun `$shelly-stack:setup-shelly-stack`.

Call `list_agents` to inspect current collaboration capacity before fan-out. Spawn independent work together only up to the available child slots, then refill a rolling window. Collaboration subagents can share a checkout, so give concurrent writers non-overlapping ownership or prepare separate git worktrees. After `wait_agent` reports an update, consume the separately delivered terminal result, then review every diff and write the parent summary yourself. A second opinion uses a different accepted model or effort pair when available; otherwise use a fresh inherited reviewer.

## Writing the reply

Write the reply clean as you draft it. A cleanup pass after drafting does not remove these patterns.

- **Short declarative sentences.** One thought per sentence, ended with a period.
- **No long-dash character anywhere.** Write a file-list bullet as a sentence ("`main.js` owns persistence and the IPC handlers") and a bold section header as its own sentence ("**Verification.** End to end via CDP").
- **A colon as a mid-sentence connector is also out** (unslop rule 14). A colon before a list is fine.
- **Terse is not an excuse to drop content.** Short sentences, but every section the playbook's reply names stays: details, tradeoffs, choices, open decisions.
- **Frame impact for the consumer and the maintainer.** Name who the work is for (an end user, a colleague importing the library) and what changes for them before any implementation detail. Then what the next engineer who owns this code inherits. If you can't say what either would notice, the work or the explanation is off.
- **Never fabricate a link, citation, or transcript reference.** Link only artifacts you produced or read this session.

Every playbook ends with a reply written this way. Include a PR link only when the authorized workflow actually created or inspected that PR. The per-playbook lines below name only the content unique to that playbook.

## Comments

Comments follow the same rule as the reply. Write them clean as you go. Keep a comment only for a non-obvious *why* the code can't show. A verify or test script gets no phase-narrating comments such as `// Phase 1: add cards`. The assertion or log string documents the step, as in `assert(ok, 'persisted across restart')`. This applies to every file you produce, including the delegate's diff.

## Playbooks

Start the native runtime contract's planning branch with the matched playbook's steps copied verbatim. Put them before task-specific items and before task-specific reasoning. A step you choose not to do stays in the list with a one-line `skip: <reason>`. Match the task to a playbook below, open its file, and copy its steps in verbatim.

A large or cross-cutting effort (a migration across many call sites, an ambitious multi-part change), or work the user steps away from to trust later, routes to the **[figure-it-out](references/routed/figure-it-out/workflow.md)** skill even when a narrower playbook like Feature fits. Use **[figure-it-out](references/routed/figure-it-out/workflow.md)** whenever no bundled playbook fits. It designs a bespoke, rigorous playbook for the task. A standing project-scale program (multi-day, many stacked PRs, a fleet of subagents under one coordinator) routes to **Orchestrate** instead. figure-it-out designs one bespoke run, orchestrate runs the program.

- **Ticket.** A bare Linear Dev ticket ID is read-only context. An explicit [`$shelly-stack:ticket DEV-99`](references/routed/ticket/workflow.md) or request to work, drive, or update the ticket routes to the **[ticket](references/routed/ticket/workflow.md)** skill and authorizes its ticket and PR lifecycle, except merging still requires an explicit land or merge request. Follow-up issue creation requires the request to authorize it.
- **Investigation.** Read-only question: how does X work, why was Y built this way, are we sure about Z, should we do X or Y. `playbooks/investigation.md`.
- **Bug fix.** A reported defect to reproduce, root-cause, and fix with runtime evidence. `playbooks/bug-fix.md`.
- **Perf issue.** A measured slowness to trace and improve against a baseline. `playbooks/perf-issue.md`.
- **Hillclimb.** Sustained, scientific improvement of one metric against a target: loop hypotheses with before/after measurement, a decision log, and one verified accepted win per iteration. Create commits only when authorized. Distinct from Perf issue, which is a one-off fix. `playbooks/hillclimb.md`.
- **Runtime forensics.** Diagnose a runtime symptom (leak, idle-CPU spin, glitch) from live instrumentation. The deliverable is a diagnosis, not a fix. `playbooks/runtime-forensics.md`.
- **Trace forensics.** Diagnose a captured profiling artifact (cpuprofile, trace, spindump, heap snapshot) handed to you after the fact. The deliverable is a diagnosis, not a fix. `playbooks/trace-forensics.md`.
- **Feature.** New or changed behavior, built from a named data shape. `playbooks/feature.md`.
- **Refactoring.** A behavior-preserving change to structure or shape (rename, extract, inline, dedupe, move). `playbooks/refactoring.md`.
- **Prototype.** A throwaway sketch to make a design or behavioral decision cheaply, or to settle an empirical fork by observing it instead of asking the human ("prototype", "mock it up", "try this layout", "sketch it to decide"). `playbooks/prototype.md`.
- **Visual parity.** Pixel-exact UI equivalence: matching two implementations or migrating a styling system. `playbooks/visual-parity.md`.
- **Authoring or modifying a skill.** Writing or editing a SKILL.md. `playbooks/authoring-a-skill.md`.
- **Eval.** Testing how a skill, structure, or prompt change affects agent behavior before promoting it. `playbooks/eval.md`.
- **Babysit.** Driving a PR or a stack to merge-ready: conflicts, review threads, CI. `playbooks/babysit.md`.
- **Shipping.** The half after Babysit. Independently verifying a green stack, then landing the contiguous verified run with gh merge-when-ready. `playbooks/shipping.md`.
- **Autonomous run.** A long task to drive to completion without stopping ("run until done", "keep going until X"). `playbooks/autonomous-run.md`.
- **Orchestrate.** A standing project handed to one coordinator chat: multi-day, many stacked PRs, dozens to hundreds of subagents, minimal human turns ("run this whole project", "own this migration until it lands"). Distinct from Autonomous run, which drives one task to a predicate. Work one agent could finish inside the session's budget routes there, not here, however program-shaped the phrasing sounds. `playbooks/orchestrate.md`.
- **Autopilot-full.** A queue of independent PRs run to merged with full autonomy. One owner per PR carries build through merge, and the root swarm-verifies each merge-ready head before its owner merges ("autopilot this queue", "full autopilot", one-owner-per-PR programs). `playbooks/autopilot-full.md`.
- **Autopilot-stack.** A queue of changes built and verified with full autonomy, delivered as one linear reviewed stack of PRs the operator lands herself ("autopilot-stack", "stack them, don't ship", "build the stack, I'll land it"). `playbooks/autopilot-stack.md`.
- **Session pickup.** Resuming or taking over a prior agent's in-flight work from a transcript or pushed branch. `playbooks/session-pickup.md`.
- **Pause safely.** Suspending in-flight work cleanly so it can be resumed, on an explicit pause, going offline, a Codex restart, or imminent context compaction. The complement to Session pickup. Full steps: `playbooks/pause-safely.md`.
- **Multi-phase or multi-PR plan.** Work that spans phases or stacked PRs. `playbooks/multi-phase-plan.md`.
- **Disk usage audit.** A read-only inventory for "what's using my disk". Route to `playbooks/worktree-cleanup.md` in audit-only mode and stop before proposing commands.
- **Worktree and simulator cleanup.** An explicitly destructive request such as "clean up worktrees", "prune safe-to-prune worktrees", "free up space", or "delete old simulators". Route to `playbooks/worktree-cleanup.md`; it still requires confirmation of the exact targets before deletion.
- **Opening a PR.** Invoked only when the current request explicitly authorizes creating and pushing a PR. Otherwise finish with verified local changes. `playbooks/opening-a-pr.md`.
