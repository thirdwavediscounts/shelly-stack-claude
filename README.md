# shelly-stack

this repository is the Claude Code plugin for shelly-stack, forked from [pstack](https://github.com/cursor/plugins/tree/main/pstack) (upstream MIT, by poteto / Lauren Tan). The Codex plugin lives in its own repository, `shelly-stack-codex`, and is maintained separately. A change that applies to both clients is ported by hand.

shelly-stack is Sean's fork of pstack for Third Wave Discounts: poteto's playbooks and principles, adapted to how we ship.

there's a growing sense that ai writes too much slop code. we agree. if you want to go fast, go deep first.

**shelly-stack helps you write less, but higher quality code.** it turns your coding agent into a real engineering team. the goal is not to maximize loc, in fact it's the opposite.

**shelly-stack gives you fearless parallelism.** when you can go deep on one agent and trust it to write good, verifiable code, you can truly parallelize with confidence. start multiple agents up with `shelly-mode` and trust that they'll apply rigorous engineering principles to their work.

**multi-model work gives you the best of all worlds.** every frontier model has strengths and weaknesses. use any model available in your client.

fork it. improve it. make it yours. PRs are welcome! 

## install

```bash
/plugin marketplace add thirdwavediscounts/shelly-stack-claude
/plugin install shelly-stack@shelly-stack
```

For a local checkout, run `/plugin marketplace add /absolute/path/to/shelly-stack-claude` instead.

## cleanup, verification, CI, and PR workflows

shelly-stack includes the team-kit workflows, adapted from Third Wave Discounts' MIT-licensed Team Kit fork (see [LICENSE.team-kit](LICENSE.team-kit)). Invoke them like any other skill, for example `/shelly-stack:deslop`. Existing project verification skills remain the first choice.

| Work | Skills |
|---|---|
| Code cleanup and review | `deslop`, `thermo-nuclear-code-quality-review`, `typescript-conventions` |
| Evidence and app control | `verify-this`, `control-ui`, `control-cli`, `run-smoke-tests`, `check-compiler-errors` |
| CI and conflicts | `fix-ci`, `loop-on-ci`, `fix-merge-conflicts` |
| PR preparation | `review-and-ship`, `new-branch-and-pr`, `make-pr-easy-to-review`, `get-pr-comments`, `pr-review-canvas` |
| Work history | `weekly-review`, `what-did-i-get-done`, `workflow-from-chats` |

## get started

two steps:

1. run [`/setup-shelly-stack`](./skills/setup-shelly-stack/SKILL.md), then choose your models.
2. use [`/shelly-mode`](./skills/shelly-mode/SKILL.md) whenever the task requires rigor.

new here? use `/shelly-guide <what you're trying to do>`. it hands you the skills for that stage. the [Claude guide](./docs/guide/README.md) walks through a first real task.

that's it. the other skills are situational; the mode skill uses them as needed. unconfigured roles keep their Anthropic defaults.

## usage

use [`/shelly-mode`](./skills/shelly-mode/SKILL.md) at the start of a task. it reads your request, picks from a set of playbooks, and runs the other skills as the steps need them.

### just use [`/shelly-mode`](./skills/shelly-mode/SKILL.md)

this skill is the main shortcut. i use it whenever i need the agent to do rigorous engineering work. it comes with twenty-three playbooks:

```
/shelly-mode this pr has a subtle bug where the scroll drifts every 750ms even when idle. repro
first, then fix and verify.
```

```
/shelly-mode i'm going to bed. land the stack even if ci flakes. i want everything merged by
morning.
```

<details>
<summary>the twenty-three playbooks</summary>

| playbook | for |
|---|---|
| [investigation](./skills/shelly-mode/playbooks/investigation.md) | a read-only question. how does x work, why was y built this way, are we sure. |
| [bug fix](./skills/shelly-mode/playbooks/bug-fix.md) | reproduce a defect, root-cause it, and fix with runtime evidence. |
| [perf](./skills/shelly-mode/playbooks/perf-issue.md) | trace a measured slowness and improve it against a baseline. |
| [hillclimb](./skills/shelly-mode/playbooks/hillclimb.md) | sustained, scientific improvement of one metric against a target, looping hypotheses with before/after measurement and one commit per accepted win. |
| [runtime forensics](./skills/shelly-mode/playbooks/runtime-forensics.md) | diagnose a live symptom (leak, idle-cpu spin, glitch) from instrumentation. |
| [trace forensics](./skills/shelly-mode/playbooks/trace-forensics.md) | diagnose a captured profiling artifact (cpuprofile, trace, spindump, heap snapshot). |
| [feature](./skills/shelly-mode/playbooks/feature.md) | new or changed behavior, built from a named data shape. |
| [refactoring](./skills/shelly-mode/playbooks/refactoring.md) | a behavior-preserving change to structure or shape. |
| [prototype](./skills/shelly-mode/playbooks/prototype.md) | a throwaway sketch to make a design or behavioral decision cheaply, or to settle an empirical fork by observing it. |
| [visual parity](./skills/shelly-mode/playbooks/visual-parity.md) | pixel-exact ui equivalence between two implementations. |
| [authoring a skill](./skills/shelly-mode/playbooks/authoring-a-skill.md) | writing or editing a SKILL.md. |
| [eval](./skills/shelly-mode/playbooks/eval.md) | test how a skill or prompt change affects agent behavior, blinded. |
| [opening a pr](./skills/shelly-mode/playbooks/opening-a-pr.md) | turn finished work into a reviewable pr: small ordered commits, clean diff, open items folded in before merge. |
| [babysit](./skills/shelly-mode/playbooks/babysit.md) | drive a pr or a stack to merge-ready: conflicts, review threads, ci. |
| [shipping](./skills/shelly-mode/playbooks/shipping.md) | independently verify a green stack, then land the contiguous verified run with graphite merge-when-ready. |
| [autonomous run](./skills/shelly-mode/playbooks/autonomous-run.md) | drive a long task to completion without stopping. |
| [orchestrate](./skills/shelly-mode/playbooks/orchestrate.md) | a standing project handed to one coordinator chat: multi-day, many stacked prs, fleets of subagents. |
| [autopilot-full](./skills/shelly-mode/playbooks/autopilot-full.md) | run independent prs to merged with one owner per pr and root verification of each merge-ready head. |
| [autopilot-stack](./skills/shelly-mode/playbooks/autopilot-stack.md) | build and verify one linear graphite stack for the operator to review and land. |
| [session pickup](./skills/shelly-mode/playbooks/session-pickup.md) | resume or take over a prior agent's in-flight work. |
| [pause safely](./skills/shelly-mode/playbooks/pause-safely.md) | suspend in-flight work cleanly so it can be resumed later. |
| [multi-phase plan](./skills/shelly-mode/playbooks/multi-phase-plan.md) | work that spans phases or stacked PRs. |
| [worktree cleanup](./skills/shelly-mode/playbooks/worktree-cleanup.md) | reclaim disk by pruning merged or abandoned worktrees and stale ios simulators, safety-gated. |

</details>



when invoked it:

1. opens the client's native plan. the first item is reading the inline principles index in the skill.
2. matches your task to a [playbook](./skills/shelly-mode/playbooks/) and copies the steps in verbatim.
3. routes to the other skills as the steps fire.
4. writes unslopped replies framed for the consumer and the maintainer.

the full rules and playbooks live in [`plugins/shelly-stack-claude/skills/shelly-mode/SKILL.md`](./skills/shelly-mode/SKILL.md).

[`/shelly-mode`](./skills/shelly-mode/SKILL.md) applies to the turn where you invoke it. Invoke it again when a later task needs it.

For long work, use `/loop`.

## skills

[`/shelly-mode`](./skills/shelly-mode/SKILL.md) runs most of these for you when a step needs them (`how`, `why`, `architect`, `arena`, `swarm`, `interrogate`, `unslop`, `no-comments`, `technical-writing`, `tdd`, and the principles). the table below is for when you want one directly:

```
/how do we cancel runs? do we have an n+1 when we look up every run to cancel?
```

```
/interrogate review this pr.
```

<details>
<summary>all skills</summary>

| skill | use it when |
|---|---|
| [`/shelly-mode`](./skills/shelly-mode/SKILL.md) | default entry point for any non-trivial task. |
| [`/shelly-guide`](./skills/shelly-guide/SKILL.md) | you don't know shelly-stack yet. names the skills for the stage you're at (understand, design, build, verify, ship, overnight) with a prompt for your task, then runs the first one. |
| [`/how`](./skills/how/SKILL.md) | you want a walkthrough of how a subsystem works. |
| [`/why`](./skills/why/SKILL.md) | you want to know why something was built this way. discovers available MCPs at run time and queries each evidence category in parallel (source control, issue tracker, long-form docs, real-time chat, infra observability, error tracking, analytics warehouse). |
| [`/recall`](./skills/recall/SKILL.md) | you're starting or resuming work and want your recent context on a topic rebuilt from your own chat history and the shared record, handed back as a tight current-state brief. |
| [`/blast-radius`](./skills/blast-radius/SKILL.md) | you have a small-looking change and want to know what else it could break, with the one fact it's safe because of proven by running code, not asserted. |
| [`/architect`](./skills/architect/SKILL.md) | you're about to write code that crosses a function boundary and want the caller's usage, types, and module shape settled first. |
| [`/arena`](./skills/arena/SKILL.md) | you want N parallel attempts at the same thing, then to grab the best parts of each. |
| [`/swarm`](./skills/swarm/SKILL.md) | you want N parallel workers across different slices or races, then one aggregated report. |
| [`/interrogate`](./skills/interrogate/SKILL.md) | you have a diff and want several different models to try to break it, including a strict code-quality lens. |
| [`/automate-me`](./skills/automate-me/SKILL.md) | you want your own `-mode` skill, drafted from how you've actually worked. |
| [`/setup-shelly-stack`](./skills/setup-shelly-stack/SKILL.md) | you want to pick which models shelly-stack uses per role. detects your models and writes a config rule. |
| [`/reflect`](./skills/reflect/SKILL.md) | a long task landed and you want the recipe captured as a skill edit. |
| [`/teach`](./skills/teach/SKILL.md) | you want to actually understand a change or subsystem, not just have it summarized. runs how + why and weaves one plain explanation, built up diagram by diagram. |
| [`/tdd`](./skills/tdd/SKILL.md) | you're fixing a bug and there's a cheap local test path. write the failing test first, then the fix. |
| [`/no-comments`](./skills/no-comments/SKILL.md) | strip comments before review; spawns Comment Sicko, fixes accepted findings, offers encodings for claimed constraints. |
| [`/typescript-best-practices`](./skills/typescript-best-practices/SKILL.md) | you're reading or editing typescript. grounds the type-system-discipline principle in syntax. |
| [`/figure-it-out`](./skills/figure-it-out/SKILL.md) | no bundled playbook fits. designs a rigorous, auditable playbook for the task. |
| [`/show-me-your-work`](./skills/show-me-your-work/SKILL.md) | you want a reviewable decision trail. logs decisions to a tsv you can commit. |
| [`/create-verification-skill`](./skills/create-verification-skill/SKILL.md) | your project has no scripted way to prove app behavior. generates a project-local verify skill with a feature map, for any language or platform. |
| [`/maintain-verification-skill`](./skills/maintain-verification-skill/SKILL.md) | your verify skill's feature map has drifted from the app. source wave + one live pass, at most one PR of proven corrections. |
| [`/unslop`](./skills/unslop/SKILL.md) | you're cleaning up writing. removes AI tells. |
| [`/bro`](./skills/bro/SKILL.md) | you want the last message restated in plain human language, no jargon. |
| [`/technical-writing`](./skills/technical-writing/SKILL.md) | layered doc standard (Diátaxis + Google developer style + STE + Global English) for docs, RFCs, readmes, PR descriptions, commit messages. |

</details>



### examples

mostly i type [`/shelly-mode`](./skills/shelly-mode/SKILL.md) at the start of a task and let it route to a playbook. the other skills fire as the steps need them. a few i reach for directly.


<details>
<summary>all the examples</summary>

```
bug fix:           /shelly-mode this pr has a subtle bug where the scroll drifts every 750ms even
                   when idle. repro first, then fix and verify.
perf:              /shelly-mode a big list takes a second or two to load even though we virtualize.
                   run a cpu trace and tell me why.
feature:           /shelly-mode build a small feature behind a feature flag. verify it really works.
prototype:         /shelly-mode build two prototypes of the markdown renderer so we can compare.
                   spawn an agent for each.
multi-phase:       /shelly-mode open source these skills as a plugin. nothing internal leaks, work
                   in a temp dir, show me the dependency graph first.
overnight run:     /shelly-mode i'm going to bed. land the stack even if ci flakes. i want
                   everything merged by morning.
babysit:           /shelly-mode check on pr 123. anything outstanding?
visual parity:     /shelly-mode the row spacing is too tall when this flag is on. the second image
                   is correct. repro and fix until it matches.
figure it out:     /shelly-mode i'm stepping away. migrate every caller from the synchronous store
                   to the new async one, keeping behavior identical. i want to trust it was done
                   right when i'm back.
how:               /how do we cancel runs? do we have an n+1 when we look up every run to cancel?
why:               /why is this feature flag not on yet?
architect:         design this instrumentation to be high signal with no false positives. /architect
                   this first.
arena:             /arena take my prompt to the arena verbatim. i want to compare their proposals
                   with yours.
swarm:             /swarm check every package under packages/ against its check.sh. one worker per
                   package. one report.
interrogate:       /interrogate review this pr.
tdd:               /tdd implement
unslop:            can we unslop and tighten the new changes?
reflect:           /reflect that took too long. capture what we learned so the next run doesn't
                   repeat it.
show-me-your-work: /show-me-your-work keep a decision trail i can review when i'm back.
automate-me:       /automate-me
```

</details>

## the `shelly-agent` and Comment Sicko subagents

shelly-stack also ships a subagent prompt that runs my style end to end. it's exposed as [`subagent_type: "shelly-stack:shelly-agent"`](./agents/shelly-agent.md).

[`/shelly-mode`](./skills/shelly-mode/SKILL.md) and [`subagent_type: "shelly-stack:shelly-agent"`](./agents/shelly-agent.md) route through the same wrapper.

shelly-stack also ships [Comment Sicko](./agents/comment-sicko.md). usually invoke it through [`/no-comments`](./skills/no-comments/SKILL.md), not directly.

## principles

twenty-one short skills, one principle each. `shelly-mode` indexes them inline and reads that index at task start. the standalone files are there so other skills can reference a principle by name, and so the index can point at the full rule for each.

<details>
<summary>all twenty-one principles</summary>

| principle | group | rule |
|---|---|---|
| [laziness-protocol](./skills/principle-laziness-protocol/SKILL.md) | core | Bias toward deletion and the smallest change that solves the problem. |
| [foundational-thinking](./skills/principle-foundational-thinking/SKILL.md) | core | Apply before writing logic: choosing core types and data structures, sequencing scaffold-vs-feature work, asking what concurrent actors share. Get the data structures right so downstream code becomes obvious. |
| [redesign-from-first-principles](./skills/principle-redesign-from-first-principles/SKILL.md) | core | Redesign as if the requirement had been a foundational assumption from day one, instead of bolting it on. |
| [subtract-before-you-add](./skills/principle-subtract-before-you-add/SKILL.md) | core | Remove dead weight, redundant validators, and stub references first, then build on the simpler base. |
| [minimize-reader-load](./skills/principle-minimize-reader-load/SKILL.md) | core | Count layers between question and answer, and hidden state in the reader's head; collapse one-caller wrappers and shrink mutable scope. |
| [outcome-oriented-execution](./skills/principle-outcome-oriented-execution/SKILL.md) | core | Apply during planned rewrites and migrations with explicit phase boundaries. Converge on the target architecture; don't preserve smooth intermediate states with throwaway compatibility code. |
| [experience-first](./skills/principle-experience-first/SKILL.md) | core | Choose user delight over implementation convenience; ship fewer polished features over more rough ones. |
| [exhaust-the-design-space](./skills/principle-exhaust-the-design-space/SKILL.md) | core | Build 2-3 competing prototypes and compare side by side before committing. |
| [build-the-lever](./skills/principle-build-the-lever/SKILL.md) | core | Apply to any non-trivial work, not just bulk work: edits, migrations, analyses, checks. Build the tool that does it or proves it (codemod, script, generator, or a skill your subagents follow) instead of working by hand. The tool is the artifact a reviewer can rerun. |
| [model-the-domain](./skills/principle-model-the-domain/SKILL.md) | architecture | Encode the domain in a structure instead of scattered conditionals. |
| [boundary-discipline](./skills/principle-boundary-discipline/SKILL.md) | architecture | Concentrate guards at system boundaries (CLI, config, network, external APIs); trust internal types and keep business logic in pure functions. |
| [type-system-discipline](./skills/principle-type-system-discipline/SKILL.md) | architecture | Make illegal states unrepresentable, brand semantic primitives, parse external data at boundaries, refuse to lie to the compiler, exhaust variants, derive from authoritative schemas. |
| [make-operations-idempotent](./skills/principle-make-operations-idempotent/SKILL.md) | architecture | Converge to the same end state regardless of partial prior runs. |
| [migrate-callers-then-delete-legacy-apis](./skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md) | architecture | Migrate callers and delete the old API in the same wave instead of preserving compatibility layers. |
| [separate-before-serializing-shared-state](./skills/principle-separate-before-serializing-shared-state/SKILL.md) | architecture | Eliminate the sharing first; serialize structurally only when one shared writer is a real invariant. |
| [prove-it-works](./skills/principle-prove-it-works/SKILL.md) | verification | Apply after completing a task, before declaring done. Verify against the real artifact (run the feature, read the actual value, inspect the diff), not a proxy, self-report, or 'it compiles.'. |
| [fix-root-causes](./skills/principle-fix-root-causes/SKILL.md) | verification | Trace each symptom to its root cause and fix it there; reproduce first, ask why until you reach it, resist nil-check guards that silence crashes. |
| [sequence-verifiable-units](./skills/principle-sequence-verifiable-units/SKILL.md) | verification | Apply to multi-step work (sweeps, migrations, runs of similar edits) and to how you stack commits and PRs. Break work into small units that each end in a verifiable state, check each before the next, and order delivery so the sequence proves itself to a reviewer. |
| [guard-the-context-window](./skills/principle-guard-the-context-window/SKILL.md) | delegation | Route bulk to subagents; keep summaries in the main thread, not raw payloads. |
| [never-block-on-the-human](./skills/principle-never-block-on-the-human/SKILL.md) | delegation | Proceed, present the result, let the human course-correct after the fact; reserve confirmation for irreversible actions. |
| [encode-lessons-in-structure](./skills/principle-encode-lessons-in-structure/SKILL.md) | meta | Encode the rule as a lint, metadata flag, runtime check, or script instead of more text. |

</details>

## why are there no planning skills?

Claude Code has plan support that works with shelly-stack. but personally, i don't believe in planning. the best spec is code. if you do want to make a plan, [`/shelly-mode`](./skills/shelly-mode/SKILL.md) covers it, but it's not a default.

## make it yours

`shelly-mode` is my style. you may not want exactly that.

type [`/automate-me`](./skills/automate-me/SKILL.md). it mines your recent transcripts, drafts a `<your-name>-mode` skill from how you've actually worked, and routes through shelly-stack underneath. you keep shelly-stack as the base and end up with your own routing skill alongside `shelly-mode`.

models are configurable too. run [`/setup-shelly-stack`](./skills/setup-shelly-stack/SKILL.md). it writes `~/.claude/rules/shelly-stack-models.md`.

## license

MIT
