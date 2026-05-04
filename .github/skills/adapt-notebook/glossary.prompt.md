---
description: Generate the contents of the `inject:glossary` cell — a small bridge table from the learner's field to the canonical ML vocabulary.
---

# glossary — field ↔ ML bridge cell

You are filling in a single markdown cell that sits near the top of the
adapted notebook, right after the intro. Its purpose: when the learner first
encounters a canonical ML term later in the notebook, they have already seen
it linked to something they recognise from their own field.

## Inputs you have in context

- `skill/canonical_terms.yaml` — the locked vocabulary, split into
  `regression` and `deep_learning` sections.
- The base notebook's top-level metadata field `adapt_sections`, which lists
  exactly which YAML sections apply to that notebook (e.g. `["regression"]`
  for notebook 01, `["deep_learning"]` for notebook 02).
- The learner's `background.md`.

## What to produce

A markdown cell whose body is exactly:

````markdown
## Glossary — your field ↔ ML

A short bridge between the vocabulary you already know and the ML terms used
below. The right-hand column uses the canonical ML names; we will not change
those, but you can mentally read the left-hand column instead whenever it
helps.

| Your field | ML term | Short bridge |
|------------|---------|--------------|
| <field word or phrase> | <canonical ML term> | <one-line connection> |
| ... | ... | ... |
````

## Rules

- **Every canonical ML term for the sections listed in the notebook's
  `adapt_sections` metadata must appear in the `ML term` column,
  spelled exactly as in the YAML.** Do not omit any. Do not rename any.
- The `Your field` column must use real vocabulary from the learner's
  background — names of techniques, instruments, quantities, processes they
  actually use. Do not invent fake jargon. If you cannot find a tight
  match for a term, write `(no close match)` in the `Your field` column —
  but the ML term still appears.
- Keep each `Short bridge` to one sentence.
- Do **not** add commentary outside the table other than the two-line
  preamble shown above.
