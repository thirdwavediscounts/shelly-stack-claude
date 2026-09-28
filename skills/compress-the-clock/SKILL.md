---
name: compress-the-clock
description: "Get a result now that would otherwise take hours or days of waiting. Force the expiry on a copy of the state, replay past instances of the event, fit the boundary inside a short run, or force time at the scheduler. Use when you are about to write or plan 'wait until', 'after <date>', 'check back', 'when the batch closes', 'the N-day loop will show', 'can only be settled by waiting', 'ready after <time>', or a follow-up to verify on a later date, and when the user asks 'can't we force a test' or 'why wait'. Not for waits on a human, a review, or a deploy you can watch finish."
---

# Compress the clock

A check that needs hours or days of wall-clock time usually has a version that runs in minutes. Before you schedule a check, date a ticket, or leave a loop running to see what happens, try the techniques below. Put on a date only what they cannot reach.

| The wait is for | Technique |
|---|---|
| A credential, session, or cache to expire | Force the expiry on a copy |
| An event that has not happened yet (closings, deliveries, batch results) | Replay past instances |
| A boundary partway through a long run (token TTL, rate-limit window, session rotation) | Put the boundary inside a short run |
| A scheduler to pick an item up | Force time where the timing decision happens |

## Force the expiry on a copy

1. List every credential's lifetime. Print names, domains, and expiry, never values. A longer-lived fallback may make the wait moot.
2. Copy the state. On the copy, delete, back-date, or corrupt the credential that is supposed to expire.
3. Run the real entry point against the copy. Check that real calls still succeed afterward, not only that the refresh step returned 200.

**Example.** A 60-minute session token was forced to expire on copies. Listing lifetimes first found a sibling refresh token that lasts about a year, which changed the plan.

## Replay past instances

The event you are waiting for has usually happened before. Run the reader on those instances.

- The account's own history.
- Sequential ids just below the open ones.
- Closed or archived records.

Check each result against an independent second source. When none exists, check an internal invariant, such as a final price no lower than the last bid.

**Example.** Instead of waiting for an evening batch of auction closings, the reader ran on the account's own closed bids and on ids just below the open lots.

## Put the boundary inside a short run

Start the run already past the boundary, for example with an expired token, instead of launching a long run and hoping it crosses. Save results per item as they arrive, so a failure keeps the partial work.

**Example.** A long run died at the 60-minute token expiry and lost every result because it saved only at the end.

## Force time where the timing decision happens

Time bugs live in the code that decides what is due. Use a fake clock, or replay stored sweeps through the real due or scheduling rule. Handing the worker a list you built by hand skips that code.

**Example.** A lot that closed early was never scheduled for capture. Only a replay of stored sweeps through the due rule caught it.

## Forcing against live state

A copy of the client's state is not isolated from the server. The copy holds live credentials.

1. Classify each server call the forced run makes as read-only or state-changing. Refresh-token rotation and single-use tokens are state-changing.
2. Check the live credential before and after the forced run.
3. Send forced-run writes to a separate output directory, so the live loop never treats them as done.
4. Pace requests so the live loop keeps working.

## Scheduler and selector

A pass that processed zero items is not evidence the schedule works. Before you trust a schedule, run its due or selection logic over stored history now and check which items it picks.

## Date only the remainder

After forcing, list what the forced test could not reach, such as a server-side lifetime or revocation. Put only that on a date. Each dated item names the alert or log field that will reveal a failure, and who reads it.

## Reply

- Each wait you started with, and the technique that replaced it.
- What the forced or replayed run showed, with the real output.
- The remainder on a date, with its alert or log field and its reader. If nothing remains, say so.
