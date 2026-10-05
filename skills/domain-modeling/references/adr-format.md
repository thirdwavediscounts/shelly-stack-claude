# ADR format

ADRs live in `docs/adr/` (or the context's own `docs/adr/`) as `0001-slug.md`, `0002-slug.md`. Find the highest number in the directory and add one.

```md
# <Short title of the decision>

<One to three sentences. The context, what we decided, and why.>
```

A one-paragraph ADR is complete. Add these sections only when they change what a reader would do:

- `Status` frontmatter (`proposed`, `accepted`, `deprecated`, `superseded by ADR-NNNN`) when the decision may be revisited.
- `## Considered options` when a rejected option would otherwise be suggested again.
- `## Consequences` when a downstream effect is not obvious.

## When a decision earns an ADR

All three must hold:

1. It is hard to reverse.
2. A future reader would be surprised by it without context.
3. There were real alternatives and the choice had specific reasons.

Examples that qualify:

- A constraint the code cannot show, such as "marketplace sync leaves `sales.product_id` NULL so only a human links a sale".
- A deliberate departure from the obvious path, such as manual SQL instead of a generated client, with the reason.
- A technology choice with lock-in, such as the auth provider or the job runner.
- A boundary decision, such as which app owns a table and which apps only read it.
