---
name: domain-modeling
description: >-
  Build and sharpen a project's shared vocabulary in GLOSSARY.md and record hard-to-reverse
  decisions as ADRs. Use when a term means different things to the user and the code, when
  naming a new domain concept, when writing or editing a GLOSSARY.md or an ADR, or when the
  grilling skill runs in a repository. Merely reading GLOSSARY.md for vocabulary is not this skill.
---

# Domain modeling

Keep one shared language between the user, the agents, and the code. Challenge fuzzy or conflicting terms while the design is discussed, and write each settled term and each hard-to-reverse decision down as it is settled. Agents that share the vocabulary write shorter answers and name code consistently.

Adapted from Matt Pocock's `domain-modeling` skill (MIT, see `LICENSE.mattpocock-skills`).

## Where the files live

- A single-context repository has one `GLOSSARY.md` at the root and ADRs in `docs/adr/`.
- A monorepo or multi-context repository has `GLOSSARY-MAP.md` at the root. It lists each context, the path of its `GLOSSARY.md` (for example `apps/<app>/GLOSSARY.md`), and how the contexts relate. Each context may keep its own `docs/adr/`. System-wide ADRs stay in the root `docs/adr/`.
- Pick the context the current topic belongs to. If two contexts fit, ask.

Create a file only when you have an entry to put in it. When the project's instructions restrict new documentation files, put the proposed entry in the reply and write it only after the user says yes.

## During the discussion

1. **Check terms against the glossary.** When the user uses a term in a way that conflicts with `GLOSSARY.md`, say so at once. "The glossary defines a relist as X, but you seem to mean Y. Which is it?"
2. **Sharpen fuzzy words.** When one word covers two things, propose a canonical term for each. "Do you mean the eBay listing or the inventory product? Those are different rows."
3. **Test the terms with concrete cases.** Invent edge cases that force the boundary between two concepts. "A sale arrives for an item that was relisted twice. Which listing does it link to?"
4. **Check the code.** When the user states how something works, read the code or the database. Surface any contradiction with the evidence.
5. **Write the glossary entry right away.** Use [`references/glossary-format.md`](references/glossary-format.md). The glossary holds definitions only, never implementation details or plans.
6. **Offer an ADR sparingly.** Offer one only when the decision is hard to reverse, surprising without context, and the result of a real trade-off. If any of the three is missing, skip it. Use [`references/adr-format.md`](references/adr-format.md).

## Reply

- Each term added or changed, with its file path.
- Each ADR written or proposed, with its path and one line on the decision.
- Any contradiction between the user's account and the code that is still open.
