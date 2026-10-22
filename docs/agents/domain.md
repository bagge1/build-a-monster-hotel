# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`GLOSSARY.md`** at the repo root.
- **`docs/GDD.md` §18, Decision log**: August's dated rulings. They play the part ADRs play elsewhere; this repo has no `docs/adr/`. Read the rulings that touch the area you're about to work in, and the GDD § a code comment points to (grep for the §, never read the whole file).

If `GLOSSARY.md` doesn't exist, **proceed silently**. Don't flag its absence; don't suggest creating it upfront. The `/domain-modeling` skill (reached via `/grill-with-docs` and `/improve-codebase-architecture`) creates it lazily when terms actually get resolved.

## File structure

Single-context repo:

```
/
├── GLOSSARY.md
├── docs/
│   └── GDD.md          ← §18 Decision log: the rulings
└── src/
```

## Decisions are August's

A decision is recorded only as a dated ruling of August's in `docs/GDD.md` §18. Never create `docs/adr/` or an ADR file. When `/domain-modeling` or another skill would record a decision, propose the ruling to August with a recommendation; once he has decided, add it to §18 in his words, with the date.

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `GLOSSARY.md`. Don't drift to synonyms the glossary explicitly avoids. The game's own English names for its things stay English, also in Swedish text.

If the concept you need isn't in the glossary yet, that's a signal: either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ruling conflicts

If your output contradicts a ruling in §18, surface it explicitly rather than silently overriding:

> _Contradicts GDD §18 (2026-10-19, the 12-stud cell), but worth reopening because…_
