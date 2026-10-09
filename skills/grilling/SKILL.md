---
name: grilling
description: >-
  Interview the user in rounds about a plan, design, or ticket until every decision in it is settled.
  Use for "grill me", "grill this plan", "interview me about X", "stress-test my thinking", or when
  the Feature playbook or the ticket skill finds open product decisions while the user is present.
  Not for facts the agent can look up or observe.
argument-hint: "[the plan, idea, or ticket to grill]"
---

# Grilling

Interview the user until you both agree on every decision the plan depends on. Treat the plan as a tree of decisions. Each decision can open further decisions that depend on its answer. In a repository, also invoke the **domain-modeling** skill so terms the interview settles get written down.

Adapted from Matt Pocock's `grilling` skill (MIT, see `LICENSE.mattpocock-skills`).

## Facts are yours, decisions are theirs

Before a question goes to the user, classify it.

- A fact you can read from code, a database, a log, or a connected tool is yours. Dispatch a subagent to find it, or look it up yourself. Never ask the user for it.
- A fact you can observe by running something (timing, layout, output) is also yours. Settle it with the Prototype playbook. Read `../shelly-mode/playbooks/prototype.md` with the Read tool. Do not call the Skill tool for shelly-mode.
- A product, scope, or preference call is the user's. Only these go in a round.

A lookup that is still running holds back only the questions that depend on it. Ask the rest now.

## Rounds

1. Map the decisions the plan contains. The frontier is every open decision whose prerequisites are already settled.
2. Ask the whole frontier in one message, in this format. Number every question and give your recommended answer.

   ```
   **Q1. <short title>**
   <the question, with the options when there are options>

   Recommended: <your answer and the one-line reason>

   ---

   **Q2. <short title>**
   ...
   ```

3. Wait for the answers. A question whose answer depends on another open question in the same round belongs in a later round.
4. Update the tree. Settled decisions open new questions and may close others. Compute the new frontier and ask the next round.
5. Stop when the frontier is empty and nothing is silently assumed. Show the decision list and ask the user to confirm it before you act on it.

Write every question in plain words. Name the concrete case ("a seller relists an item that already sold") instead of an abstract category.

## Reply

Each round is the numbered questions only. After the last round, reply with:

- The settled decisions, one line each.
- What you will do next with them (the playbook, the ticket update, or the spec).
- Any glossary entries or ADRs the **domain-modeling** skill wrote or proposed.
