---
name: adapt-notebook
description: Adapt the base ML/DL notebooks (notebooks/01_simple_regression.ipynb, notebooks/02_deep_learning_regression.ipynb) to a learner's background while preserving canonical ML terminology byte-identically. Use when the user asks to "adapt the notebook", "personalize this tutorial", "rewrite for my field", or provides a `background.md` and points at one of the base notebooks.
---

# adapt-notebook — personalize the ML/DL tutorial without losing the fundamentals

## When to use

Invoke when the learner wants the base tutorial notebooks re-explained in the
vocabulary and examples of their own field (biochemistry, astrophysics,
clinical research, economics, anything else). The result is a new `.ipynb`
that:

- keeps every code cell **unchanged**,
- keeps every cell tagged `keep:code`, `lock:terms`, or any other `keep:*` /
  `lock:*` tag **byte-identical**,
- rewrites only `adapt:*` cells (including `adapt:narrative`) with
  field-specific framing,
- inserts a field↔ML glossary at the `inject:glossary` placeholder,
- contains every canonical term from `skill/canonical_terms.yaml` verbatim.

A separate validator (`scripts/validate_adapted.py`) enforces all of this.
**Your output must pass the validator.**

## Recommended models

Use whatever model the learner has selected in VS Code — the skill works with
any modern chat model. For best results:

- **Claude Sonnet 4.5** — default; great at following the per-cell constraints.
- **Claude Opus 4.7** or **GPT-5.5** — when the learner wants particularly
  rich, domain-specific analogies and is happy to wait.
- Smaller / local models are fine for iterating; expect to re-run the
  validator more often.

## End-to-end "new persona" workflow (recommended entry point)

When a learner asks to adapt the notebooks for themselves — even if they
haven't prepared any files — run this full flow:

### Step 1 — Gather background
- If the learner has already provided background text (pasted CV, short bio,
  or a filled-in `background.md`), proceed to Step 2.
- Otherwise run [`interview.prompt.md`](interview.prompt.md) to gather it
  interactively (one question at a time).

### Step 2 — Derive persona slug and write background.md
- From the field name, derive a short `snake_case` folder name
  (e.g. "Marine Biologist" → `marine_biologist`).
- Write the background to `examples/<slug>/background.md` using the template
  in `interview.prompt.md`.

### Step 3 — Adapt both base notebooks in order
For each base notebook (`01_simple_regression.ipynb`, then
`02_deep_learning_regression.ipynb`):
1. Read `skill/canonical_terms.yaml` and `examples/<slug>/background.md`.
2. Read the base notebook from `notebooks/`.
3. Process every cell using the dispatch table below.
4. Write the output to `examples/<slug>/<notebook_name>.ipynb`.
5. Run the validator:
   ```bash
   python scripts/validate_adapted.py notebooks/<nb> examples/<slug>/<nb>
   ```
6. If validation fails, fix only the flagged cells and re-validate.

### Step 4 — Execute notebooks to embed outputs
After both notebooks pass validation, run:
```bash
source .venv/bin/activate && jupyter nbconvert --to notebook --execute \
  --inplace --ExecutePreprocessor.timeout=120 \
  examples/<slug>/01_simple_regression.ipynb \
  examples/<slug>/02_deep_learning_regression.ipynb
```

### Step 5 — Done
Tell the learner their notebooks are ready at `examples/<slug>/` and
offer to open them.

---

## Inputs (single-notebook mode)

1. `background.md` — the learner's background (paste from CV or short
   description). If missing or shorter than ~80 words, run
   [`interview.prompt.md`](interview.prompt.md) first to fill it in.
2. A base notebook path, e.g. `notebooks/01_simple_regression.ipynb`.
3. An output path, e.g. `examples/biochemist/01_simple_regression.ipynb`.

## Pipeline (high level)

For each cell of the base notebook, dispatch by its tag:

| Tag                 | Action |
|---------------------|--------|
| `lock:terms`        | Copy verbatim. **Never edit.** Pure ML vocabulary / formulas. |
| `keep:code`         | Copy verbatim. Clear outputs. |
| `inject:glossary`   | Replace cell content with output of [`glossary.prompt.md`](glossary.prompt.md). |
| `adapt:narrative`   | Rewrite via [`rewrite-cell.prompt.md`](rewrite-cell.prompt.md) with `tag=narrative`. Title, story, and section-intro cells. |
| `adapt:context`     | Rewrite via [`rewrite-cell.prompt.md`](rewrite-cell.prompt.md) with `tag=context`. **Field-specific bridge** placed immediately after each `lock:terms` subtopic — translates the locked definitions into the learner's working vocabulary. |
| `adapt:intro`       | Rewrite via [`rewrite-cell.prompt.md`](rewrite-cell.prompt.md) with `tag=intro`. |
| `adapt:explanation` | Rewrite via [`rewrite-cell.prompt.md`](rewrite-cell.prompt.md) with `tag=explanation`. |
| `adapt:example`     | Rewrite via [`rewrite-cell.prompt.md`](rewrite-cell.prompt.md) with `tag=example`. |
| `adapt:exercise`    | Rewrite via [`rewrite-cell.prompt.md`](rewrite-cell.prompt.md) with `tag=exercise`. |
| `adapt:suggestions` | Generate via [`suggestions.prompt.md`](suggestions.prompt.md). |
| `adapt:code-comment`| Rewrite **only the comments** inside the code; the code body must AST-compare equal to the original. |

Then write the output notebook (preserving cell order, types, tags, and
metadata) and run:

```bash
python scripts/validate_adapted.py <BASE> <OUT>
```

If validation fails, read the error, re-do only the offending cells, and
re-validate. Do not work around the validator — it is the contract.

## Hard rules (enforced by the validator)

1. **Do not add, delete, or reorder cells.** One in, one out, in the same
   position with the same tags.
2. **Do not modify code.** Comments inside `adapt:code-comment` cells may
   change; the executable code must remain AST-equivalent.
3. **Every canonical term in `skill/canonical_terms.yaml` must appear
   verbatim** somewhere in the adapted notebook. You may add field-specific
   words *alongside* (e.g. "the **target** — what biochemists would call the
   measured response") but never *instead of*.
4. **`lock:*` cells are sacred.** They define shared terminology and math.
   Two adaptations of the same base notebook must contain byte-identical
   `lock:terms` cells (and any other `lock:*` / `keep:*` cells).
5. The `inject:glossary` cell must include a small markdown table with
   columns `Your field` | `ML term` | `Short bridge`.

## Suggested orchestration

The simplest reliable flow inside Copilot Chat:

1. Read `skill/canonical_terms.yaml` and the learner's `background.md` once
   into your working context.
2. Read the base notebook with `read_file` (it is JSON; treat each cell as a
   unit).
3. For each cell, follow the dispatch table above, generating the new
   `source` while preserving `cell_type`, `metadata.tags`, and (for code
   cells) clearing `outputs` and `execution_count`.
4. Write the new notebook to the output path.
5. Run the validator from the integrated terminal.
