### Multi-phase or multi-PR plan

Before an authorized commit, run `$shelly-team-kit:deslop` on the scoped code diff. Keep the prose pass through **[unslop](../references/routed/unslop/workflow.md)**. Use the companion control skills only when the project verification skill lacks a suitable harness, following Shelly Mode's Companion skills section.

**You own the plan, not the code. The plan is a checklist an owner runs box by box and the operator audits from the evidence.** The plan is the deliverable. Do not implement.

1. When the change is one or two files with an obvious approach, skip the plan. Say so and stop.
2. Settle open questions by prototype before you write. Run `./prototype.md` for each. Keep the scratch path and observed output or screenshots for Appendix A. Do not create a branch or commit the prototype unless the current request explicitly authorizes those history actions. Ask the operator only about a product or preference call that no run can settle. Give options (the **[never-block-on-the-human](../references/routed/principle-never-block-on-the-human/workflow.md)** principle skill).
3. Explore in subagents with a Shelly worker prompt that requires reading `$shelly-stack:shelly-mode` in full and an explicit model per the Subagents section (the **[guard-the-context-window](../references/routed/principle-guard-the-context-window/workflow.md)** principle skill). Each returns file pointers, conventions, test commands, and entry points. No inlined dumps.
4. Copy the skeleton below into the plan file and fill every placeholder. Unless the operator names a path, write the file under `~/.codex/shelly-stack/plans/<project-slug>/`. Keep every heading and every sub-block in the order shown. One section per PR. One PR is one change with its own evidence (the **[sequence-verifiable-units](../references/routed/principle-sequence-verifiable-units/workflow.md)** principle skill). Name the execution playbook in **How to read this**. Pick between `./autopilot-full.md` and `./autopilot-stack.md` per the rule at the end of `./autopilot-stack.md`. A standing program takes `./orchestrate.md`.
5. Write under [`$shelly-stack:technical-writing`](../references/routed/technical-writing/workflow.md) in full, then [`$shelly-stack:unslop`](../references/routed/unslop/workflow.md). The body is one Diátaxis mode, how-to. Appendices hold explanation and reference. No abstract metaphors; short declarative sentences. Each heading states the task or the finding. No long dashes. No mid-sentence colons.
6. Resolve the installed Shelly Stack `shelly-mode` skill directory, then run `node <shelly-mode-skill-dir>/scripts/check-plan.mjs <plan.md>` and fix every line it prints (the **[encode-lessons-in-structure](../references/routed/principle-encode-lessons-in-structure/workflow.md)** principle skill). It enforces the skeleton's shape, the verification rule in every verification block, and the punctuation rules.
7. Hand back. Post the plan path and the script's output, then stop. Execution starts on the operator's explicit go, under the execution playbook the plan names.

**Verification.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked (the **[prove-it-works](../references/routed/principle-prove-it-works/workflow.md)** principle skill). That sentence is the verification rule. Every verification block opens with it. The live block is mandatory. Ten lanes using the configured implementation role pair or native runtime fallback at the PR head drive the real surface through its verification skill, per the **[swarm](../references/routed/swarm/workflow.md)** skill. Each lane is one box with a concrete scenario, the screenshot it saves, and its pass predicate. One lane is the **Regression lane against trunk.** It runs the same load-bearing scenario on trunk and head. If trunk does not have the feature, the lane records that fact and gates the behavior the diff adds plus the end state the user waits for instead of inventing a trunk result. The perf gate is dual-sided. Trunk and head must both produce the named metric. If trunk lacks the feature, also isolate the work the diff adds and set an absolute budget for that work plus the end-to-end state the user waits for. Do not claim a ratio between unlike scenarios. The perf block names the metric, the interleaved probe, the trunk baseline measured first, and the rule with the number that fails. A PR that changes an interaction is review-gated. The operator reviews it in chat with screenshots and a video before merge. A PR that changes no interaction writes `**Review gate.** None. <PR id> is not review-gated.` and no boxes under it.

**Verification skill.** Pick it by surface. Browser, Electron, and web UIs use the project's browser verification skill. CLIs and TUIs use its CLI verification skill. Generate either with [`$shelly-stack:create-verification-skill`](../references/routed/create-verification-skill/workflow.md). Native mobile uses whatever simulator-driving skill the repo has. A PR that touches two surfaces gets lanes on both. A surface with no verification skill is a risk in Appendix C, and its live block still names how each lane drives it.

````markdown
# <Program> plan

<Under ten lines. What changes, for whom, the rule the program enforces, and the PR ids in order.>

## How to read this

One box is one unit of work. Every box names the evidence that checks it. A nested box is a sub-step of the box above it. Check a box only when its evidence exists, a file, a log line, a screenshot, a test run, or a SHA. The body is a how-to. The appendices explain and record.

The program runs `<shelly-mode-skill-dir>/playbooks/<execution playbook>.md`. <Who merges, and which PR ids are the operator's items that stop at merge-ready.>

Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

## Program checklist

### Arm the program

- [ ] State this plan and every history or external action it would take (commit, rebase, push, open or retarget a PR, post a comment or message, update a ticket, merge), then stop. Start only when the operator's explicit go authorizes those action classes; otherwise keep output local.
- [ ] On her go, record this exact text through the native runtime contract's planning branch. Use its persistent-goal branch only when she explicitly asks for persistence across turns. "<The plan path, the PR ids in order, the verification rule, who merges, and the done condition.>"
- [ ] Resolve the installed Shelly Stack skill directory. Read the bundled execution playbook, `swarm`, `opening-a-pr`, and every other bundled leaf skill from that installed package at program start and every audit.
- [ ] Read the project-local verification skill from the working tree. Use `git show origin/main:<verification skill path>` only when comparing it with the project's base branch.
- [ ] Use `wait_agent` for active owners. If the operator explicitly requested recurring future audits, use the native runtime contract's recurring-check branch. Never leave the cadence to memory when that branch is available.
- [ ] Use this tick prompt, verbatim. "Re-read the installed execution playbook and the recorded program objective. Audit the operation against both and fix drift in this tick. Probe every active lane and judge progress by side effects only. Stand down a stuck lane and dispatch its replacement now. Then send the operator a status message, whether or not anything changed, with the queue table of PR, owner, state, and head SHA, the verdicts since the last tick, what merged, open operator gates, and blockers."
- [ ] On the operator's hold or stand-down, send every owner a zero-writes order at once.

### Spawn owners

- [ ] Spawn one owner per PR with the full lifecycle the execution playbook names.
- [ ] Follow this dependency graph. Start dependent work only after its parent merges, or base it on the parent branch when the execution playbook stacks.
  - [ ] <PR id> and <PR id> are independent and first. Both branch from `main`.
  - [ ] <PR id> after <PR id>.
- [ ] Hold the file boundaries. <PR id or class> touches only `<glob>`.
- [ ] Hold the review gate. <PR ids> change an interaction. They wait for the operator's review in chat with screenshots and a video before merge.

### PR mechanics, for every PR

- [ ] Resolve the forge once. Test Origin first with `command -v origin` and an authenticated read-only repository lookup. If both succeed, use `origin pr` for every PR operation. Otherwise require `command -v gh`, `gh auth status`, and `gh repo view --json nameWithOwner`; use `gh` only when all three succeed for the current repository. If neither forge is available, authenticated, and repository-accessible, stop before the first PR operation and report the missing prerequisite. Never require `gt`.
- [ ] Open the PR ready, never draft, with `origin pr create --status open --base <base-branch>` or `gh pr create --base <base-branch>` according to the resolved forge, and `draft: false`. A stack child targets its parent branch.
- [ ] Run the repo's lint and typecheck once before the PR-facing push. Push with hooks on.
- [ ] Run `<shelly-mode-skill-dir>/references/routed/unslop/workflow.md` before each commit and `<shelly-mode-skill-dir>/references/routed/no-comments/workflow.md` before review.
- [ ] Run a native Codex review on the PR branch. Triage every finding and every security-reviewer comment per `<shelly-mode-skill-dir>/references/bugbot-triage.md`.
- [ ] Rebase onto current trunk before babysit and again before the merge-ready report.

### Verdict and merge, for every PR

- [ ] At the merge-ready head SHA, run the workflow at `<shelly-mode-skill-dir>/references/routed/swarm/workflow.md`. One gates lane. The ten live lanes from the PR's **Verify, live** block. The perf lane from its **Verify, perf** block. One audit lane that reads the diff and the receipts and distrusts the PR body.
- [ ] Clean only when every lane is `PASS`. Findings go back to the owner. A new head gets a fresh swarm and a fresh verdict.
- [ ] <The merge or append rule from the execution playbook, with the patch-id rule from `<shelly-mode-skill-dir>/playbooks/shipping.md`.>

### Boot recipe, for every live lane

Each live lane runs in a dedicated git worktree that the parent prepares at the PR head before spawning. Drive through the project's verification skill.

- [ ] `git fetch origin <head-branch> && git checkout <head SHA>`.
- [ ] <Start the backend and the surface. Wait for ready.>
- [ ] <Deliver input only through the verification skill's commands. Name the read-only diagnostics.>
- [ ] Save every screenshot to `/tmp/swarm-<pr-id>/worker-<n>/<slug>.png` and return the paths with the report.

## <Task as a verb phrase> (<PR id>)

**Depends on.** <PR id, or None.>

**Files.**

- [ ] Edit `<path>`.
- [ ] Create `<path>`.
- [ ] Delete `<path>`.

**Build.**

- [ ] <One change. Name the symbol and the file.>

**You see.**

- [ ] <One observable result, with the exact log line or screen state.>

**Verify, unit.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

- [ ] <Test file and the case it gains.> Run `<command>`.

**Verify, live.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked. Ten lanes using the configured implementation role pair or native runtime fallback at the PR head, per the boot recipe.

- [ ] Lane 1. Regression lane against trunk. Run <the same load-bearing scenario> at trunk and head. If trunk lacks the feature, record that and gate <the behavior the diff adds plus the end state the user waits for>. Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 2. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 3. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 4. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 5. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 6. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 7. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 8. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 9. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 10. <Scenario.> Save `<slug>.png`. Pass when <predicate>.

**Verify, perf.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

- [ ] Metric. <What is measured at both trunk and head. If trunk lacks the feature, also name the diff-added work and the end-to-end state the user waits for.>
- [ ] Probe. <The command or procedure, run at trunk and at the head, interleaved. Both sides must produce the metric.>
- [ ] Baseline. Record the trunk <value> first.
- [ ] Rule. <Head against trunk, with the number that fails. If the scenarios differ, add absolute budgets for the diff-added work and the user-visible end state instead of an invalid ratio.>

**Review gate.** The operator reviews before merge.

- [ ] Copy lane <n> screenshots into `<media path>/<pr-id>-review-<slug>.png`.
- [ ] Record a 30 to 60 second video of the change from a lane worktree. Save it as `<media path>/<pr-id>-review.mp4`.
- [ ] Post the screenshots and the video in chat. Stop at merge-ready. Wait for the operator's click.

**Merge.**

- [ ] Root's clean verdict at the exact head SHA.
- [ ] Native Codex review findings triaged.
- [ ] Rebased onto current trunk after the verdict, patch-id unchanged.
- [ ] <The owner squash-merges its own PR, or the root appends it to the base-branch stack and the operator lands it bottom-up.>

## Close the program

- [ ] Every box above is checked with its evidence.
- [ ] Reply to the operator with the report the execution playbook names.

## Appendix A. Prototype evidence

<Each open question a prototype answered, with its scratch path and observed output or artifact links. Include a branch or commit reference only when that history action was explicitly authorized. Each question that stays unproven.>

## Appendix B. Alternatives rejected

<Each approach weighed and why it lost.>

## Appendix C. Risks

<Each risk with the PR it lands in and what the owner watches.>

## Appendix D. Links and reading list

<Docs to read before editing. Which PRs use `<shelly-mode-skill-dir>/references/routed/how/workflow.md` and `<shelly-mode-skill-dir>/references/routed/interrogate/workflow.md`. The trail uses `<shelly-mode-skill-dir>/references/routed/show-me-your-work/workflow.md`.>
````

**Reply:** the plan path, the PR ids with their dependencies and the review-gated set, what the prototypes proved and what stays unproven, and the check script's output.
