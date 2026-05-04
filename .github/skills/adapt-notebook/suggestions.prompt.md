---
description: Generate the `adapt:suggestions` block — a small set of copy-pasteable prompts the learner can paste into any LLM (ChatGPT, Claude, Mistral, ...) to explore a concept in depth, then return to the notebook.
---

# suggestions — "Go deeper with an LLM" block

You are filling in one `adapt:suggestions` cell. Its job: give the learner
2–4 ready-to-paste prompts they can drop into whatever chat LLM they prefer
to explore the concept just covered, then return to the notebook.

## Inputs you have in context

- The **previous cell's source** — this tells you which canonical ML
  concept(s) the learner just met. Center the suggestions on those.
- The learner's `background.md`.
- `skill/canonical_terms.yaml`.

## Output format (markdown cell body)

````markdown
### Go deeper with an LLM (optional — skip if you already know this)

If a concept above feels new, paste any of the prompts below into your
preferred chat model (ChatGPT, Claude, Mistral, ...), explore until you are
satisfied, then come back here and continue.

**Prompt 1 — <one-line topic>**
```
<a fully self-contained prompt the learner can paste verbatim>
```

**Prompt 2 — <one-line topic>**
```
<...>
```

**Prompt 3 — <one-line topic>**
```
<...>
```
````

## Rules for each prompt

1. **Self-contained.** The prompt must make sense pasted into a fresh chat
   with no prior context. Mention the canonical ML term explicitly.
2. **Tied to the learner's field.** Ask for an explanation that uses a
   concrete example from their background. (If their field is unclear,
   default to "with a concrete example from <field from background.md>".)
3. **Asks for depth, not just a definition.** Ask for the *why*, an edge
   case, a worked numerical example, or a comparison.
4. **Ends with a return cue.** The last sentence of each prompt should be
   along the lines of: *"Keep the answer to ~5 minutes of reading so I can
   return to my notebook."*
5. **Uses the canonical ML term verbatim** as it appears in
   `canonical_terms.yaml`.

## How many prompts

- 2 prompts for short concepts (one canonical term).
- 3–4 prompts when the previous cell introduced several terms together
  (e.g. forward pass + backward pass + optimizer).

Do not output anything outside the markdown cell body.
