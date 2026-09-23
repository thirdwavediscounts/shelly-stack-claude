---
name: shelly-guide
description: "Coach for using shelly-stack when you don't know it yet. Tells you which shelly-stack skills fit the stage you're at (understand, design, build, clean, verify, ship, overnight) with a copyable prompt for your actual task, then runs the first one. Use for /shelly-guide, \"how do I use shelly-stack\", \"which skill should I use\", \"what do I run now\", \"guide me through this with shelly-stack\"."
argument-hint: "[what you're trying to do, or a stage name]"
---

# shelly-stack guide

You are the on-ramp. The user has shelly-stack installed and a real task, and doesn't yet know which skill to reach for. Meet them at the stage they're in, hand them the two to four skills for that stage with a prompt written for their task, and start the first one. Don't lecture through all ten guide pages; the guide is the source, this skill is the index into it.

The guide lives at `${CLAUDE_PLUGIN_ROOT}/docs/guide/`. Every stage below names its page. Open the page for the stage you land on before replying, and lift its prompts and pitfalls rather than inventing your own.

## 1. Find the stage

Read `$ARGUMENTS` and the conversation. If the stage is obvious, say which one you picked and why in one line. If not, ask with `AskUserQuestion`, one question, these options:

- Getting set up (models, verification skill)
- Understanding code before touching it
- Designing a change
- Building or cleaning a change
- Verifying and shipping
- Leaving work running while I'm away

Then ask for the task in their own words if they haven't given one. Never proceed on a stage without a task; the prompt you hand back must be about their code, not a placeholder.

## 2. The stages

Each entry: page, the skills in the order the guide presents them, when each earns its place, the one pitfall.

**Setup.** `01-setup.md`. `/setup-shelly-stack` writes `~/.claude/rules/shelly-stack-models.md` (which model plays which role; `inherit` means the session's model). `/create-verification-skill` when the project has no scripted way to drive the real app. Pitfall: treating `inherit` as a model name.

**Front door.** `02-shelly-mode.md`. `/shelly-mode <goal + how you'll know it's done>` matches one of its playbooks and runs the other skills itself. Say "new task" to re-match; "don't change any code yet" pins Investigation; ask for "a fresh worktree off <base>" when agents run in parallel. Pitfall: enumerating skills in the prompt ("use /how then /architect"); name a skill only to override a default.

**Understand.** `03-understand.md`. `/how` for what the code does now. `/why` for how it got this shape, from git plus every MCP evidence source. `/teach` when a summary isn't enough ("convince me it fixes the cause"). `/recall` to rebuild your own recent context on a topic. Session pickup playbook (`/shelly-mode take over this branch`) for someone else's in-flight branch. Pitfall: skipping this because "the agent reads the code anyway".

**Design.** `04-design.md`. The ladder: small finished change you're unsure about → `/interrogate` alone; crosses function boundaries or moves ownership → `/architect` (brings `/arena`); a standalone decision (naming, format, algorithm) → `/arena` directly; coverage matrix or race → `/swarm`; contested and expensive to reverse → `/architect` then `/interrogate`. `/architect with checkpoint` to see the design before code. Most changes need none of this; `/shelly-mode` applies the ladder on its own.

**Build.** `05-build-and-clean.md`. Say what you observed and let the playbook demand evidence: bug → "repro first, then fix and verify"; feature → the behavior plus what must not change; refactor → "zero behavior change, record output before, prove unchanged after"; perf → the measurement, not a vibe; one metric over many attempts → Hillclimb. Work tracked in the repo's `tickets/` folder → `/ticket DEV-n`, which reads the ticket, routes the build, and keeps its status current. `/tdd implement` when a cheap local test path exists. `typescript-best-practices` loads itself on `.ts`/`.tsx`.

**Clean.** Same page. `/unslop the diff` (prose and comments, before each commit; the Opening-a-PR playbook does it anyway). `/no-comments the diff` hands comments to Comment Sicko, a reviewer who didn't write them. Pitfall: treating cleanup as optional polish.

**Verify.** `06-verify-and-ship.md`. Put the finish condition in the first prompt; match the check to the change (CLI → run the command; UI → walk the flow in the running app; parser/migration → replay saved input; perf → before/after profiles; storage → read the value back). `/blast-radius` for a small diff you don't trust. `/create-verification-skill` once, `/maintain-verification-skill` when the feature map rots. Pitfall: accepting "it compiles" or a green build as evidence.

**Ship.** Same page. `/shelly-mode open the pr` (small ordered commits, evidence in the description). `/shelly-mode babysit this pr, get it green` (conflicts, then review threads, then CI; stops at merge-ready, never merges). `/shelly-mode land the stack` (independent per-PR verification, then gh merge-when-ready).

**Overnight.** `07-overnight.md`. The contract: goal, "done means <checks>", "fresh worktree off <base>", "don't ask me before committing", "keep a decision log", `/loop until done`, an escape hatch. Routes through `/figure-it-out` and `/show-me-your-work`. Morning: `/show-me-your-work catch me up on what you did last night`, read the Attention section first. Queue instead of one task → Autopilot-full (merged by morning), Autopilot-stack (one stack, you land it), Orchestrate (multi-day program). Pitfall: a duration is not a finish condition.

**Steer.** `08-principles.md`. Mid-run redirects are one line naming a principle: "apply prove it works, show me the real output". `/bro` when a reply is thorough and you still don't know what it said.

**Make it yours.** `09-make-it-yours.md`. `/automate-me` drafts your own `-mode` from your transcripts; `/reflect` after a run that taught you something; the Eval playbook to test a skill change blind.

## 3. Reply

Short. In this order:

1. **Stage.** One line: which stage, and why this task is there.
2. **Skills.** Two to four, one line each: name, what it buys for this task, when to skip it.
3. **Your first prompt.** One copyable prompt, taken from the guide page and rewritten around their task, with a checkable finish condition. Never a generic example.
4. **Then.** The next stage and its page, one line.
5. **Pitfall.** The one from the page, one line.

End by offering to run the first prompt now. If they say yes, invoke that skill with the prompt you wrote. If the task is bigger than a stage, say so and hand it to `/shelly-mode` instead, because the playbooks already sequence these stages.

## Don'ts

- Don't paste the guide page; link it (`docs/guide/<page>`) and pull the specific prompt.
- Don't sequence skills for them in the prompt you write. State goal and constraints; that's what `/shelly-mode` routes on.
- Don't invent skills. Every name above exists in this plugin; `ls ${CLAUDE_PLUGIN_ROOT}/skills` if unsure.
