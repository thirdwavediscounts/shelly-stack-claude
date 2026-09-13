---
name: recall
description: Reconstruct recent working context from the current Codex task, related task history, memory, live repository state, and shared records. Use for catch-me-up and resume requests.
---

# Recall

Rebuild the user's recent working context and return a tight current-state brief before new work starts. Read only the threads and records needed for the named topic.

1. Classify the request. Use the `session-pickup` playbook for one known task. Use `automate-me` for durable working preferences. If the user already supplied a complete state capsule, use it and skip history mining.
2. Fix the scope. Default to the active workspace and the last seven days. State any different topic, workspace, or time window the user requested. Never turn “all” into a bounded window silently.
3. Read Codex history safely. Prefer the current conversation, native `list_threads` and `read_thread` when available, and the provided memory index. Otherwise use a parent-provided narrow digest or an exact user-supplied task/session path. Never discover or scan unrelated `~/.codex/sessions/` records. For a large in-scope corpus, split the supplied material among read-only native subagents and keep raw transcripts out of the parent context.
4. Search the shared record when the topic names a feature, file, subsystem, or bug. Route source control, issues, long-form docs, chat, observability, and error tracking through the **why** skill's investigators. Treat unavailable sources and null results as findings.
5. Verify live state. Check surfaced branches, PRs, tickets, files, and runtime status with current tools. A prior task summary is history, not proof of the present state.
6. Write the brief through the **unslop** skill and cite the task, memory, PR, ticket, or external record that supports each consequential claim.

## Output

- **Capsule:** at most five bullets covering the goal and current state.
- **Threads:** one line each with `[merged #N]`, `[open PR #N]`, `[in flight <branch>]`, `[verified, uncommitted]`, `[reverted #N]`, or `[planned, not started]`.
- **Problems:** at most five recurring blockers, including reverted fixes or ongoing user symptoms.
- **Next move:** one concrete action.

Keep adjacent work out unless it blocks the named topic. Sanitize private context before public output.
