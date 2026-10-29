### Investigation

**You own the answer. Plan, route, write.**

Investigation requests are read-only. They produce a cited explanation or a recommendation, not a code change.

1. For a question about live behavior (what runs, when, how long, how many), check the sources in Bug fix step 1 (`playbooks/bug-fix.md`) before you read any code. For how a subsystem works, call the Skill tool with `shelly-stack:how`. For why it was built that way, call it with `shelly-stack:why`. A question that one or two files answer needs neither call. Read them and cite `file:line`. When the answer needs many files or long logs, Read `../../principle-guard-the-context-window/SKILL.md` and send the bulk reads to `shelly-stack:shelly-reader` subagents.
2. Throughput checkpoint stays one line: `throughput checkpoint: n/a, read-only investigation`.
3. Produce the `how`-shaped output (Overview / Key Concepts / How It Works / Where Things Live / Gotchas), or a recommendation with a tradeoffs table if the request is a decision between alternatives.
4. Call the Skill tool with `shelly-stack:unslop` before you post the reply.

No PR, no babysit, no `architect` unless the investigation precedes a code change. If it does, hand back to the user and re-route to Bug fix or Feature.

**Reply:** the investigation output. For "are we sure?" answers, include your real judgment with reasons. Push back if the premise is wrong (see Autonomy).
