---
description: Rewrite a single `adapt:*` cell to suit the learner's background. Used for `adapt:narrative`, `adapt:context`, `adapt:intro`, `adapt:explanation`, `adapt:example`, `adapt:exercise`, and `adapt:code-comment` cells.
---

# rewrite-cell — per-cell rewriter

You are rewriting **one cell** of the base notebook. You receive:

- the original cell `source`,
- its tag (one of `narrative`, `context`, `intro`, `explanation`, `example`,
  `exercise`, `code-comment`),
- the learner's `background.md`,
- the canonical-terms list from `skill/canonical_terms.yaml`.

You output the new `source` for that cell. Cell type, tags, and position are
preserved by the orchestrator — do not emit JSON or metadata, just the cell
body.

## Universal rules

1. **Keep every canonical term that already appears in the original cell,
   spelled identically.** You may add a field-specific synonym alongside —
   "the **target** (what a clinician would call the *outcome*)" — but never
   replace the canonical term.
2. **Do not invent claims about the learner's field.** If you are not sure
   an analogy is correct, choose a more generic one.
3. **Match the length of the original cell**, give or take ~20%. This is a
   tutorial; do not balloon every paragraph.
4. **Replace the placeholder narrative with one rooted in the learner's
   field.** The base notebook ships with a generic placeholder story
   ("observed `x`, predict `y`"). Your job is to give the learner a
   concrete running example *from their own work* — enzyme kinetics,
   photometry, dose-response, household budgets, etc. The synthetic data
   and code stay the same; only the framing changes.
5. **Preserve all LaTeX math** in the cell exactly as written.

## Per-tag guidance

### `narrative`
This is a title, story, or section-intro cell. Replace the placeholder
framing with one that lives entirely in the learner's field. Pick **one
concrete prediction task from their daily work** (e.g. *substrate
concentration → reaction rate*, *exposure time → photon counts*, *dose →
clearance*, *income → consumption*) and use it consistently across every
`adapt:narrative` cell in the notebook. Keep the structure (heading
levels, paragraph count) identical to the original cell.

### `context`
This cell sits **immediately after a `lock:terms` cell** that just
introduced a subtopic (vocabulary, the model equation, the loss, gradient
descent, train/test split, the neural-network architecture, the training
loop, or honest evaluation). The locked cell uses pure ML vocabulary; your
job is to write a **short field-specific bridge** that says "in your
world, this is what those words actually point at". Rules:

- Keep it short (3–6 sentences, or a small bullet list).
- Start with `### In your field` (heading level 3), so it nests under the
  preceding `## ` section heading.
- Refer back to the canonical terms from the locked cell using the *same
  spelling* (bold them when first used: **feature**, **target**, **MSE**,
  **gradient descent**, etc.) and tie each one to a concrete object,
  routine, or decision from the learner's daily work.
- Where the locked cell uses variable names (`x`, `y`, `w`, `b`, `f1…f4`),
  spell out what those mean in the learner's units ("`x` is tonight's
  cover count; `y` is total prep hours").
- Do **not** restate the formal definitions — the locked cell already
  did that. You are translating, not re-teaching.

### `intro`
Use the same field-specific running task you chose for the
`adapt:narrative` cells. Add one or two sentences linking it to a
familiar situation from the learner's background. End with the same
call-to-action as the original.

### `explanation`
Re-explain the *same* concept in the learner's vocabulary. Lead with the
canonical ML term in **bold**, then bridge to the analogy. Do not introduce
new ML concepts that were not in the original cell.

### `example`
Re-frame the worked example using a quantity from the learner's field.
Keep the numbers and the conclusion identical to the original — only the
narrative around them changes.

### `exercise`
Keep the **same three exercises** the original cell asks. Re-word the
prompts to feel natural for the learner's field, but the underlying task
must be unchanged so the validator (and the learner running the code)
sees the same operations.

### `code-comment`
**This cell is a code cell, not markdown.** You may only modify lines that
begin with `#` (Python comments). Every non-comment line must be byte-
identical to the original. The validator AST-compares the code; if the AST
differs, your output is rejected.

Comments should still narrate what the code does, just in language that
helps the learner. Keep them brief.

## Output

Return only the new cell `source`. No preamble. No code fences around the
whole answer. (Inside markdown, fenced code blocks are of course fine.)
