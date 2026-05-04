---
description: Orchestrate the full adaptation — read the base notebook, dispatch each cell to the right sub-prompt, write the output notebook, and run the validator.
---

# assemble — full adaptation pipeline

This is the orchestration prompt. Use it after `background.md` exists.

## Inputs

- `BASE_NB` — path to the base notebook (e.g. `notebooks/01_simple_regression.ipynb`).
- `OUT_NB` — path where the adapted notebook should be written
  (e.g. `examples/biochemist/01_simple_regression.ipynb`).
- `background.md` at the project root.

## Steps

1. **Load context once.**
   - Read `skill/canonical_terms.yaml`.
   - Read `background.md`.
   - Read `BASE_NB`.

2. **For each cell** in `BASE_NB.cells`, in order, build a new cell:
   - `cell_type` and `metadata` are **copied unchanged** (tags must survive).
   - `outputs` and `execution_count` are cleared (set to `[]` and `null`)
     for code cells.
   - `source` is determined by the cell's tag(s):

   | Tag (first match wins) | How to produce the new source |
   |------------------------|-------------------------------|
   | `keep:core` or `keep:code` | Copy the original `source` byte-for-byte. |
   | `inject:glossary`      | Run [`glossary.prompt.md`](glossary.prompt.md). |
   | `adapt:intro`          | Run [`rewrite-cell.prompt.md`](rewrite-cell.prompt.md) with `tag=intro`. |
   | `adapt:explanation`    | Run [`rewrite-cell.prompt.md`](rewrite-cell.prompt.md) with `tag=explanation`. |
   | `adapt:example`        | Run [`rewrite-cell.prompt.md`](rewrite-cell.prompt.md) with `tag=example`. |
   | `adapt:exercise`       | Run [`rewrite-cell.prompt.md`](rewrite-cell.prompt.md) with `tag=exercise`. |
   | `adapt:suggestions`    | Run [`suggestions.prompt.md`](suggestions.prompt.md) (pass the previous cell's source as the "concept just met"). |
   | `adapt:code-comment`   | Run [`rewrite-cell.prompt.md`](rewrite-cell.prompt.md) with `tag=code-comment`. |

3. **Write `OUT_NB`** as valid `nbformat` v4 JSON. Cell count, types, and
   tags must match the base notebook exactly.

4. **Validate.** From the integrated terminal:

   ```bash
   . .venv/bin/activate 2>/dev/null || true
   python scripts/validate_adapted.py BASE_NB OUT_NB
   ```

   If validation fails:
   - Read the failure message.
   - Re-run **only** the prompt for the offending cell(s).
   - Overwrite the output notebook and re-validate.

5. **Report back** to the user with the path to the adapted notebook and
   any validator output. Suggest they open the notebook in VS Code and run
   it, or render HTML with `python scripts/render_showcase.py`.
