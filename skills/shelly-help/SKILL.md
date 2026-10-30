---
name: shelly-help
description: "Help for using shelly-stack (formerly shelly-guide): setup, /shelly-mode, and picking the skill, playbook, or principle for a task or stage (understand, design, build, clean, verify, ship, overnight), with a copyable prompt for the actual task. Use for /shelly-help, /shelly-guide, \"shelly-help\", \"shelly-guide\", \"how do I use shelly-stack\", \"which skill should I use\", \"what do I run now\", \"guide me through this with shelly-stack\", or a run that went wrong."
argument-hint: "[your question, what you're trying to do, or a stage name]"
---

# shelly-stack help

Answer the user's question about shelly-stack, hand them a prompt they can send, and link the file the answer came from. For a help question, don't start the work. The user asked how, and a shelly-stack run spends real tokens, so offer the prompt and let them say yes.

A message that asks for work, such as "use shelly-stack to fix this bug", is not a help question. Spawn a `shelly-stack:shelly-agent` subagent with the task, because that agent loads the shelly-mode rules on its own.

This file maps questions to the skills and guide pages that hold the answers. Those files own the details. Read the file you route to before you quote it, and trust it when it disagrees with this map. The guide lives at `${CLAUDE_PLUGIN_ROOT}/docs/guide/`, and skills at `${CLAUDE_PLUGIN_ROOT}/skills/`. The user may not be able to open the installed copy, so link the public one: `https://github.com/thirdwavediscounts/shelly-stack-claude/blob/main/` followed by the path.

## 1. Find out what they need

Read `$ARGUMENTS` and the conversation. A named situation, such as "which skill reviews a PR?", goes straight to its section. A named stage goes to that stage in section 4. If the need is still unclear, ask one `AskUserQuestion` with these options, then answer only the one they pick:

- Get set up
- Start a task with `/shelly-mode`
- Pick a skill for the stage I'm at
- Fix a run that went wrong
- Make shelly-stack my own

For a stage question, ask for the task in their own words if they haven't given one. The prompt you hand back must be about their code, not a placeholder.

Check the state that changes the answer, and mention it only when it does:

- No `~/.claude/rules/shelly-stack-models.md` means `/setup-shelly-stack` hasn't run for this user, so every role uses its default model.
- No `verify-*` skill or other app harness in the project means agents have no scripted way to drive the app. Mention `/create-verification-skill` when the question is about proving a change works.
- No formal verification skill in the project means no property is checked past what tests reach. Mention `/create-formal-verification-skill` when the question is about a race, an invariant, or another case tests rarely hit. When one exists and the code it covers changed after the commit it records as last in sync, mention `/maintain-formal-verification-skill` if the question touches that code.

When the model rule is missing and it matters (the user is new, the question is about setup or cost, or the answer depends on which models run), ask once per chat whether they want to pick models now. Now: give them `/setup-shelly-stack` and answer the question too. Later: answer, and add one line saying every role keeps its default until they run it.

## 2. Get set up

Page: `01-setup.md`.

1. Install with `/plugin marketplace add thirdwavediscounts/shelly-stack-claude`, then `/plugin install shelly-stack@shelly-stack`. Commands then work as `/shelly-mode` or `/shelly-stack:shelly-mode`.
2. Run [`/setup-shelly-stack`](../setup-shelly-stack/SKILL.md). It maps a model to each role and writes `~/.claude/rules/shelly-stack-models.md`. `inherit` means the role runs on the session's model; it is not a model name. A role can name a pinned agent such as `shelly-stack:shelly-opus-medium`, which fixes a model and an effort. The rule applies to new sessions.
3. Run `/create-verification-skill` when the project has no scripted way to drive the real app.
4. Start a real task with `/shelly-mode`, a goal, and a check that can pass or fail.

If cost is the worry, say where the tokens go. shelly-stack spends extra tokens on subagents and review panels. Rerun `/setup-shelly-stack` and pick cheaper models or `inherit`. A shorter panel list runs fewer subagents, one per entry. Save `/shelly-mode` for work that needs rigor.

## 3. Start a task with `/shelly-mode`

Page: `02-shelly-mode.md`. `/shelly-mode <goal + how you'll know it's done>` matches the task to a playbook, copies its steps into the todo list, and runs the other skills as the steps need them. A skipped step stays in the list as `skip: <reason>`. A good prompt states the goal and the done check. It doesn't list skills, because a hand-written order drops or reorders steps the playbook keeps. Read [`references/prompting.md`](references/prompting.md) before you help word one.

- `/shelly-mode` attaches to one message and fades as the chat moves on. Start each new task with it, or say "new task" to re-match a playbook.
- "don't change any code yet" pins Investigation.
- Ask for "a fresh worktree off <base>" when agents run in parallel.
- To get the same style from a subagent of your own, spawn it with `subagent_type: "shelly-stack:shelly-agent"`.

## 4. Pick a skill by stage

The default answer is `/shelly-mode`, which runs most of the others when its steps need them. Name a skill directly when the user wants more or less of something than the playbook gives. Each stage gives its page, the skills, and the one pitfall.

**Understand.** `03-understand.md`. `/in-your-own-words` to check the agent understood the goal and problem before it starts. `/sharpen` to rewrite a prompt deeper, not bigger; it returns the prompt and doesn't do the task. `/how` for what the code does now. `/why` for how it got this shape. `/teach` when a summary isn't enough ("convince me it fixes the cause"). `/recall` to rebuild your own recent context on a topic. `/ketchup` to catch up on this chat since your last message, with every call waiting on you; `/ketchup-video` for the same as a short subtitled video. Session pickup playbook (`/shelly-mode take over this branch`) for an in-flight branch. Pitfall: skipping this because "the agent reads the code anyway".

**Design.** `04-design.md`. `/grilling` first when the open questions are product decisions only you can make. A small finished change you're unsure about gets `/interrogate` alone. A change to a type, an exported signature, or a module boundary gets `/architect`, which brings `/arena`. A standalone decision (naming, format, algorithm) gets `/arena` directly. A coverage matrix or race gets `/swarm`. A contested design that is costly to reverse gets `/architect`, then `/interrogate`. `/architect with checkpoint` to see the design before code. Most changes need none of this.

**Build.** `05-build-and-clean.md`. Say what you observed and let the playbook demand evidence: bug, "repro first, then fix and verify"; feature, the behavior plus what must not change; refactor, "zero behavior change, record output before, prove unchanged after"; perf, the measurement, not a guess; one metric over many attempts, Hillclimb. `/tdd implement` when a cheap local test path exists. `/wizard` when setup needs keys or clicks only you can do. `/ticket DEV-123` drives a Linear ticket to a PR. `typescript-best-practices` loads itself on `.ts` and `.tsx`.

**Clean.** Same page. Before every PR, the Opening a PR playbook cuts code slop, then calls `unslop` and `no-comments`, in that order. The user does not run them by hand. For work not going through a PR yet, `/unslop the diff` cleans prose and comments, and `/no-comments the diff` hands comments to Comment Sicko, an agent that didn't write them. Pitfall: treating cleanup as optional polish.

**Verify.** `06-verify-and-ship.md`. Put the finish condition in the first prompt and match the check to the change (CLI, run the command; UI, walk the flow in the running app; parser or migration, replay saved input; perf, before and after profiles; storage, read the value back). `/benchmark-checklist` before you report or act on a perf number. `/blast-radius` for a small diff you don't trust. `/compress-the-clock` when the check would mean waiting hours or days. `/create-verification-skill` once, `/maintain-verification-skill` when the feature map drifts. `/create-formal-verification-skill` for a race, retry, or state machine tests can't reach; `/statechart` to check and draw a TLA+ model; `/maintain-formal-verification-skill` when verified code changed without a recheck. Pitfall: accepting "it compiles" or a green build as evidence.

**Ship.** Same page. `/shelly-mode open the pr` (cleanup, small ordered commits, evidence in the description, body from `/pr`). `/shelly-mode babysit this pr, get it green` (conflicts, review threads, then CI; stops at merge-ready, never merges unless asked). `/shelly-mode land the stack` (per-PR checks, then merge when ready).

**Overnight.** `07-overnight.md`. The contract: goal, "done means <checks>", "fresh worktree off <base>", "don't ask me before committing", "keep a decision log", `/loop until done`, and a way out. Routes through `/figure-it-out` and `/show-me-your-work`. Morning: `/show-me-your-work catch me up on what you did last night`, Attention section first. A queue instead of one task: Autopilot-full (merged by morning), Autopilot-stack (one stack, you land it), Orchestrate (multi-day program). Pitfall: a duration is not a finish condition.

**Steer.** `08-principles.md`. Mid-run redirects are one line naming a principle: "apply prove it works, show me the real output". `/bro` when a reply is thorough and you still don't know what it said.

Close calls:

- `/how` explains what the code does. `/why` explains the reasons. `/teach` runs one or both and explains the result plainly.
- `/arena` gives every worker the same brief and merges the best parts. `/swarm` splits work into slices or a race and returns one report.
- `/interrogate` reviews the diff. `/blast-radius` looks for breakage outside the diff and proves the one fact that makes the change safe.
- `/recall` rebuilds context across recent chats. `/ketchup` covers only this chat since the user's last message. Resuming one chat or branch is the Session pickup playbook.
- `/figure-it-out` designs one rigorous run. Orchestrate runs a program across days and many PRs. Autonomous run drives one task to a finish condition.

If a skill under `skills/` is missing here, read its frontmatter and route by its description. Never name a skill that isn't there; `ls ${CLAUDE_PLUGIN_ROOT}/skills` if unsure. `/loop` is a Claude Code built-in. Orchestrate is a `/shelly-mode` playbook, not a skill.

## 5. Playbooks and principles

Playbooks are step lists inside `/shelly-mode`, not skills, so they have no slash command. Describing the task picks one, and these phrases name one directly:

- "babysit this pr" or "check on pr 123" runs Babysit.
- "land the stack" runs Shipping.
- "take over this branch" runs Session pickup.
- "pause safely" runs Pause safely.
- "full autopilot on this queue" runs Autopilot-full. "autopilot, don't merge" runs Autopilot-stack.
- "run the eval playbook" runs Eval.
- Asking for a plan for multi-phase work runs Multi-phase plan, which writes the plan and doesn't implement it.

The Playbooks section of [`shelly-mode`](../shelly-mode/SKILL.md) lists every playbook. Principles are one-rule skills that `/shelly-mode` reads and cites. The user steers with their names, as in "apply prove it works. show me the real output." Page `08-principles.md` lists them.

## 6. Fix a run that went wrong

- The mode stopped applying after a few turns: start the next task with `/shelly-mode` again.
- A question got treated as the next step of the last task: say "new task".
- A new model choice had no effect: the rule applies to new sessions. Start one.
- Runs cost more than expected: see the cost paragraph in section 2.
- Parallel agents overwrote each other: give each agent its own worktree.
- An overnight run moved but finished nothing: `/loop` needs a check that can pass or fail, not a duration. See `07-overnight.md`.
- The reply claims success from a green build: ask for the real command, flow, stored value, or profile. That's the prove-it-works principle.
- Agents keep making the same mistake in this repo: `/correct`.

For a run that drifts, [`references/prompting.md`](references/prompting.md) has one-line steers. Page `10-recipes-and-pitfalls.md` has more pitfalls.

## 7. Make shelly-stack my own

Page: `09-make-it-yours.md`.

- `/reflect` after a session turns its lessons into skill edits the user approves.
- `/correct` turns repeated corrections into checks that make the mistake impossible.
- `/shelly-mode write a skill for <workflow>` runs the authoring playbook, which uses `/create-skill`. The Eval playbook tests a skill change blind.
- Fix a misbehaving skill in its own PR, not inside the feature work where it went wrong.

## Reply

Short. In this order:

1. **Answer.** One line. For a stage question, name the stage and why this task is there.
2. **Skills.** Two to four, one line each: name, what it buys for this task, when to skip it.
3. **Your first prompt.** One copyable prompt in a code block, adapted from [`references/recipes.md`](references/recipes.md) or the guide page and rewritten around their task, with a checkable finish condition. Never a generic example.
4. **Then.** The next stage and its page, one line.
5. **Pitfall.** The one from the page, one line.
6. **Source.** The public link to the file the answer came from.

Skip lines that don't apply to the question. End by offering to run the first prompt. If they say yes, invoke that skill with the prompt. For a `/shelly-mode` prompt, or a task bigger than one stage, spawn a `shelly-stack:shelly-agent` subagent with it.

## Don'ts

- Don't paste the guide page; link it and pull the specific prompt.
- Don't sequence skills for them in the prompt you write. State goal and constraints; that's what `/shelly-mode` routes on.
- Don't invent skills.
