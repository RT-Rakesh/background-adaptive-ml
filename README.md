# Background-Adaptive ML Notebooks

> One ML tutorial. Re-explained for your field, without losing the fundamentals.

**Live showcase → [rt-rakesh.github.io/background-adaptive-ml](https://rt-rakesh.github.io/background-adaptive-ml/)**

This repo contains two short Jupyter notebooks that teach **linear regression**
and a **tiny PyTorch neural network** through a single running story. A VS Code
Copilot Chat **skill** reads a learner's `background.md` and rewrites only the
explanation cells — analogies, worked examples, exercises, and copy-pasteable
*"go deeper with an LLM"* prompts — while a glossary-lock keeps every canonical
ML term identical across every adaptation.

Pre-rendered adaptations for five personas (biochemist, astrophysicist,
economist, clinical researcher, cook) are live at the URL above.

## Why

Tutorials that fix a single backstory ("predicting house prices...") work for
some learners and bounce off others. The *concepts* are universal. The split
this repo enforces:

- **Canonical cells** (`lock:terms`, `keep:code`) are byte-identical across
  every adaptation. The vocabulary — *loss, gradient, MSE, epoch, weights,
  hidden layer, ReLU, forward/backward pass, optimizer* — is the same for
  everyone, every time.
- **Adaptable cells** (`adapt:*`) get rewritten with analogies the learner
  recognises from their own field.
- **"In your field" bridge cells** (`adapt:context`) appear after every
  locked subtopic, translating the canonical definition into the learner's
  working vocabulary.
- **Code cells** (`keep:code`) never change. The notebook always runs.

A validator enforces all of the above before publishing.

## Try it yourself (quickest way)

Open the project in VS Code, then in Copilot Chat:

```
/adapt-notebook I'm a marine biologist studying coral reef recovery
```

The skill will interview you, write `examples/marine_biologist/background.md`,
adapt both notebooks, validate, and execute them. You can also pass a richer
description to skip most of the interview — see the [live site](https://rt-rakesh.github.io/background-adaptive-ml/) for examples.

## Layout

```
notebooks/                  # Two base notebooks (source of truth)
  01_simple_regression.ipynb
  02_deep_learning_regression.ipynb

skill/
  canonical_terms.yaml      # Locked vocabulary the validator checks for

.github/skills/adapt-notebook/
  SKILL.md                  # Copilot Chat skill entry point
  interview.prompt.md       # Background-gathering interview
  glossary.prompt.md        # Builds the field ↔ ML glossary cell
  rewrite-cell.prompt.md    # Per-cell rewriter
  suggestions.prompt.md     # "Go deeper with an LLM" prompt blocks
  assemble.prompt.md        # Orchestration

scripts/
  build_base_notebooks.py   # Regenerate the two base notebooks
  apply_persona.py          # Offline assembler for showcase examples
  validate_adapted.py       # Invariant checks + execution gate
  render_showcase.py        # nbconvert → site/
  build_all.py              # End-to-end: build, validate, render

examples/<persona>/
  background.md             # Learner background
  *.yaml                    # Cell-by-cell content overrides
  *.ipynb                   # Adapted & executed notebook

site/                       # Static showcase (rebuilt by CI)
  index.html
  <persona>/*.html
```

## Build locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python scripts/build_base_notebooks.py
python scripts/build_all.py          # apply personas, validate, render
```

## What the validator checks

`scripts/validate_adapted.py` rejects any adapted notebook that:

- adds, removes, or reorders cells;
- modifies a cell tagged `lock:*` or `keep:*` (byte-compared);
- modifies executable code in an `adapt:code-comment` cell (AST-compared);
- omits any canonical term from `skill/canonical_terms.yaml`;
- fails to execute end-to-end.

```bash
python scripts/validate_adapted.py \
  notebooks/01_simple_regression.ipynb \
  examples/me/01_simple_regression.ipynb
```

## Recommended models

Works with any model selected in VS Code. Best results with:

- **Claude Sonnet 4.5** — default, fast, follows per-cell constraints well.
- **Claude Opus 4.7 / GPT-5.5** — richer domain analogies, slower.
