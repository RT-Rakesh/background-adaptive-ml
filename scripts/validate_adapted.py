"""Validate an adapted notebook against its base notebook.

Checks (all must pass):
  1. Every cell tagged `keep:core` or `keep:code` is byte-identical to the
     corresponding cell in the base notebook (matched by position).
  2. Every code cell tagged `adapt:code-comment` has identical *code* (the
     AST is unchanged); only comments and whitespace may differ.
  3. Every canonical term from skill/canonical_terms.yaml appears at least
     once in the adapted notebook.
  4. The adapted notebook executes top-to-bottom without error.

Usage:
    python scripts/validate_adapted.py BASE.ipynb ADAPTED.ipynb [--no-execute]
Exit 0 on success, non-zero on the first failure.
"""

from __future__ import annotations

import argparse
import ast
import io
import re
import sys
import tokenize
from pathlib import Path

import nbformat
import yaml
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parent.parent
CANONICAL_FILE = ROOT / "skill" / "canonical_terms.yaml"


def cell_source(cell) -> str:
    src = cell.get("source", "")
    return "".join(src) if isinstance(src, list) else src


def cell_tags(cell) -> list[str]:
    return list(cell.get("metadata", {}).get("tags", []) or [])


def has_tag(cell, prefix: str) -> bool:
    return any(t == prefix or t.startswith(prefix + ":") or t.startswith(prefix) for t in cell_tags(cell))


def strip_comments_and_whitespace(code: str) -> str:
    """Return code with all comments removed and trailing whitespace
    normalised, so that comment-only edits compare equal."""
    out = []
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
    except (tokenize.TokenizeError, IndentationError):
        return code  # let the executor catch real syntax issues
    for tok in tokens:
        if tok.type == tokenize.COMMENT:
            continue
        out.append(tok)
    try:
        return tokenize.untokenize(out).strip()
    except ValueError:
        return code


def code_equivalent(a: str, b: str) -> bool:
    if strip_comments_and_whitespace(a) == strip_comments_and_whitespace(b):
        return True
    # Fall back to AST comparison (more permissive about formatting).
    try:
        return ast.dump(ast.parse(a)) == ast.dump(ast.parse(b))
    except SyntaxError:
        return False


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def check_keep_cells(base_nb, adapted_nb) -> None:
    if len(base_nb.cells) != len(adapted_nb.cells):
        fail(
            f"cell count differs: base has {len(base_nb.cells)}, "
            f"adapted has {len(adapted_nb.cells)} (the skill must not add or remove cells)"
        )
    for i, (b, a) in enumerate(zip(base_nb.cells, adapted_nb.cells)):
        b_tags, a_tags = cell_tags(b), cell_tags(a)
        if b_tags != a_tags:
            fail(f"cell {i}: tags changed (base={b_tags}, adapted={a_tags})")

        is_locked = any(t.startswith("keep:") or t.startswith("lock:") for t in b_tags)
        if is_locked:
            if cell_source(b) != cell_source(a):
                fail(f"cell {i} is tagged keep:*/lock:* but its source was modified")

        if "adapt:code-comment" in b_tags:
            if b.cell_type != "code" or a.cell_type != "code":
                fail(f"cell {i}: adapt:code-comment must be a code cell")
            if not code_equivalent(cell_source(b), cell_source(a)):
                fail(f"cell {i}: adapt:code-comment changed code, not just comments")


def check_canonical_terms(base_nb, adapted_nb) -> None:
    canonical = yaml.safe_load(CANONICAL_FILE.read_text())
    sections = base_nb.metadata.get("adapt_sections") or list(canonical.keys())
    all_terms: list[str] = []
    for section in sections:
        if section not in canonical:
            fail(f"unknown adapt_sections entry: {section}")
        all_terms.extend(canonical[section])

    full_text = "\n".join(cell_source(c) for c in adapted_nb.cells)
    missing = []
    for term in all_terms:
        # case-insensitive whole-token match (allows punctuation around it)
        pattern = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(term) + r"(?![A-Za-z0-9_])", re.IGNORECASE)
        if not pattern.search(full_text):
            missing.append(term)
    if missing:
        fail(f"canonical terms missing from adapted notebook: {missing}")


def execute_notebook(adapted_path: Path) -> None:
    nb = nbformat.read(adapted_path, as_version=4)
    client = NotebookClient(nb, timeout=120, kernel_name="python3")
    try:
        client.execute()
    except Exception as exc:
        fail(f"adapted notebook failed to execute: {exc}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("base", type=Path)
    p.add_argument("adapted", type=Path)
    p.add_argument("--no-execute", action="store_true", help="skip the execution check")
    args = p.parse_args()

    base_nb = nbformat.read(args.base, as_version=4)
    adapted_nb = nbformat.read(args.adapted, as_version=4)

    check_keep_cells(base_nb, adapted_nb)
    check_canonical_terms(base_nb, adapted_nb)
    if not args.no_execute:
        execute_notebook(args.adapted)

    print(f"OK: {args.adapted} passes all checks")


if __name__ == "__main__":
    main()
