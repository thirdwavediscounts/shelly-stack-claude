# GLOSSARY.md format

```md
# <Context name>

<One or two sentences on what this context is and why it exists.>

## Language

**Listing**:
One eBay offer for one item, active or ended.
_Avoid_: post, auction (unless the format matters)

**Relist**:
A new listing created for an item whose earlier listing ended unsold.
_Avoid_: repost, resubmit
```

## Rules

- Pick one word per concept. List the rejected synonyms under `_Avoid_`.
- Define what the term is in one or two sentences, not what the code does with it.
- Include only terms specific to this project. General programming words (timeout, retry, cache) do not belong.
- Group terms under subheadings when clusters form. A flat list is fine for a small context.

## GLOSSARY-MAP.md

A repository with several contexts has a map at the root.

```md
# Glossary map

## Contexts

- [eBay auctions](./apps/ebay-auctions/GLOSSARY.md): bidding on and tracking eBay auctions
- [Customer service](./apps/customer-service-dashboard/GLOSSARY.md): buyer messages, offers, and returns

## Relationships

- A sale synced from eBay belongs to customer service until a human links it to a product.
```

Read the map first when it exists. Otherwise a root `GLOSSARY.md` means one context.
