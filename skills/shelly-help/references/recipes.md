# Prompts worth copying

Swap in the real paths, skills, and done checks. Informal wording works.

## Understand

- `/shelly-mode read <thread>. restate the underlying issue in your own words, in plain english.`
- `/in-your-own-words <long or messy ask>`
- `/sharpen <the prompt you're about to send>`
- `/shelly-mode investigate why <symptom>. give me what we know, what data you used, and your best hypotheses. don't change any code yet.`
- `use /how to understand <subsystem>. then use /why to find out why it broke recently.`
- `/recall my work on <topic> from last week, then read <issue>.`
- `/teach me why you implemented it this way and not <other way>. what did you trade off?`
- `/shelly-mode take over this branch. read the decision log, find what's done, and continue. don't redo finished work.`

## Build

- Bug: `/shelly-mode <symptom>. repro first, then fix and verify.`
- Bug in an app: `/shelly-mode repro this with /verify-<app>. if it repros on main, fix it and show me a video as proof.`
- Bug with a cheap test: `/shelly-mode repro <bug> first. if there's a cheap test path, /tdd it. then fix and rerun.`
- Feature: `/shelly-mode add <behavior>. <current output> stays byte-identical. verify both.`
- Refactor: `/shelly-mode move <code> into one module, zero behavior change. record the current output first and prove it's unchanged after.`
- Perf: `/shelly-mode <operation> takes <time> on <fixture>. trace it, fix the measured cause, show me before and after.` Then `/benchmark-checklist` on the numbers.
- Ticket: `/ticket DEV-123`

## Design and plan

- `/shelly-mode prototype a few options for <feature>. take screenshots or videos for me to compare.`
- `/shelly-mode we need <feature>. /architect it first, and answer open questions with prototypes. let me review before proceeding.`
- `/shelly-mode write a tutorial for how i would use <new package> first. then /teach me why it beats the current one.`
- `ask /arena for a second opinion on this thread and our approach.`
- `/shelly-mode turn this design into a plan. small verifiable PRs, each with its own verification steps.`
- `/grilling this plan` when the open questions are yours to answer.

## Review and ship

- `/interrogate the whole branch, but skeptically. don't change anything yet. no nitpicks unless it's a real bug or regression.` Read the Dropped list too.
- `/blast-radius of <change>` for a small diff you don't trust.
- `/create-formal-verification-skill prove <property> holds in <module>, even when <steps> interleave or retry.` After merges or refactors in that code: `/maintain-formal-verification-skill`.
- `/swarm check every package under <dir> against its check script. one worker per package. one report.`
- `/shelly-mode open the pr. small ordered commits, evidence in the description.`
- `/shelly-mode babysit this pr. get it green.` For status only: `/shelly-mode check on pr <number>. anything outstanding?`
- `/shelly-mode land the stack.`

## Away and back

- `/shelly-mode im going to bed. <goal> in a fresh worktree off <base>. done means <checks>. keep a decision log. don't ask me before committing. /loop until done. if you're truly stuck after a few hours, stop and write up why.`
- `/show-me-your-work catch me up on what you did last night.` Read its Attention section first.
- `/ketchup` catches you up on this chat since your last message and lists every call that waits on you. `/ketchup-video` does the same as a short video.
- `/shelly-mode full autopilot on this queue. each item is independent.`
- `/shelly-mode autopilot these changes, but don't merge. i'll land them.`

## Make it yours

- `/reflect capture what we learned so the next run doesn't repeat it.` Approve only edits that change a future decision.
- `/correct` when agents keep making the same mistake in this repo.
- `/bro` restates the last reply in plain words.
