"""Apply a per-persona content override to a base notebook.

This is the offline mechanism used to build the pre-rendered showcase
examples. The interactive Copilot Chat skill is the production path; this
script just lets us check the four reference personas into git as
reproducible artifacts.

A persona override file looks like:

    background: |
      <kept for reference; not used by this script>
    glossary: |
      <full markdown body for the inject:glossary cell>
    overrides:
      "<index> adapt:intro":      "...new markdown body..."
      "<index> adapt:explanation": "..."
      "<index> adapt:suggestions": "..."
      "<index> adapt:code-comment":
        comments:
          "<original comment line stripped of leading #>": "<new comment text>"

Where <index> is the 0-based cell index in the base notebook.

For an override to apply, the (index, tag) pair must match. Any unspecified
adapt:* cell is left as-is from the base notebook (so the validator's
canonical-term checks still pass, and the behavior is predictable).

Usage:
    python scripts/apply_persona.py \\
        notebooks/01_simple_regression.ipynb \\
        examples/biochemist/01_simple_regression.yaml \\
        examples/biochemist/01_simple_regression.ipynb
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import yaml


def _split_lines(text: str) -> list[str]:
    return text.splitlines(keepends=True) or [""]


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def apply_overrides(nb: dict, overrides: dict, glossary_md: str | None) -> dict:
    out = copy.deepcopy(nb)
    for i, cell in enumerate(out["cells"]):
        tags = list(cell.get("metadata", {}).get("tags") or [])

        if "inject:glossary" in tags and glossary_md is not None:
            cell["source"] = _split_lines(glossary_md.rstrip("\n"))
            continue

        for tag in tags:
            key = f"{i} {tag}"
            if key not in overrides:
                continue
            value = overrides[key]
            if tag == "adapt:code-comment":
                cell["source"] = _rewrite_comments(cell["source"], value.get("comments", {}))
            else:
                cell["source"] = _split_lines(str(value).rstrip("\n"))

        if cell["cell_type"] == "code":
            cell["outputs"] = []
            cell["execution_count"] = None

    return out


def _rewrite_comments(source_lines: list[str], comment_map: dict[str, str]) -> list[str]:
    """Replace lines that are pure comments matching keys in comment_map.

    The key in comment_map is the comment text after the leading `#` and
    surrounding whitespace stripped. The value is the new comment text
    (also without the leading `#`). Indentation is preserved.
    """
    new_lines = []
    src = "".join(source_lines)
    for line in src.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("#"):
            indent = line[: len(line) - len(stripped)]
            comment_body = stripped.lstrip("#").strip()
            newline_suffix = "\n" if line.endswith("\n") else ""
            if comment_body in comment_map:
                new_lines.append(f"{indent}# {comment_map[comment_body]}{newline_suffix}")
                continue
        new_lines.append(line)
    return new_lines


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("base", type=Path)
    p.add_argument("override", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()

    nb = json.loads(args.base.read_text(encoding="utf-8"))
    spec = _load_yaml(args.override)

    out = apply_overrides(
        nb,
        overrides=spec.get("overrides", {}) or {},
        glossary_md=spec.get("glossary"),
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
