"""Render adapted notebooks to standalone HTML for the static showcase.

Usage:
    python scripts/render_showcase.py
Reads:  examples/<persona>/*.ipynb  (must already be executed)
Writes: site/<persona>/<notebook>.html
        site/index.html (landing page)
"""

from __future__ import annotations

import shutil
from pathlib import Path

import nbformat
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
SITE = ROOT / "site"

PERSONA_TITLES = {
    "biochemist": "Biochemist",
    "astrophysicist": "Astrophysicist",
    "economist": "Economist / Social Scientist",
    "clinical_researcher": "Clinical Researcher",
}

INDEX_CSS = """
:root { --fg: #1f2933; --muted: #52606d; --accent: #2f5d8c; --bg: #fafbfc; --card: #fff; }
* { box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       max-width: 960px; margin: 0 auto; padding: 2.5rem 1.25rem;
       color: var(--fg); background: var(--bg); line-height: 1.55; }
h1 { font-size: 2rem; margin-bottom: 0.25rem; }
.tag { color: var(--muted); font-size: 0.95rem; }
section { margin-top: 2.5rem; }
.grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
.card { background: var(--card); border: 1px solid #e4e7eb; border-radius: 10px;
        padding: 1.1rem 1.25rem; }
.card h3 { margin: 0 0 0.4rem 0; }
.card a { color: var(--accent); text-decoration: none; display: inline-block; margin-right: 0.75rem; }
.card a:hover { text-decoration: underline; }
.howto { background: var(--card); border: 1px solid #e4e7eb; border-radius: 10px;
         padding: 1.25rem 1.5rem; }
code { background: #eef1f4; padding: 0.1em 0.35em; border-radius: 4px; }
footer { margin-top: 3rem; color: var(--muted); font-size: 0.9rem; }
"""

# Gentle highlight for the per-subtopic "In your field" context cells
# and the "Go deeper with an LLM" prompt cells. Targets the cell tag
# classes emitted by nbconvert's lab template.
CONTEXT_CSS = r"""
/* Shared shape for tagged callout cells. */
.celltag_lock\:terms,
.celltag_inject\:glossary,
.celltag_adapt\:context,
.celltag_adapt\:intro,
.celltag_adapt\:example,
.celltag_adapt\:exercise,
.celltag_adapt\:suggestions,
.celltag_adapt\:narrative {
  border-radius: 6px;
  padding: 0.75rem 1.1rem;
  margin: 0.5rem 0;
}
.celltag_adapt\:context h3,
.celltag_adapt\:suggestions h3 {
  margin-top: 0.1rem;
  border-bottom: none;
}

/* Neutral warm-gray for everything structural.
   Only the two persona-bridge cells (context = amber, suggestions = violet)
   get accent colors. */
.celltag_lock\:terms,
.celltag_inject\:glossary,
.celltag_adapt\:intro,
.celltag_adapt\:example,
.celltag_adapt\:exercise,
.celltag_adapt\:narrative {
  background: #fbfaf7;
  border-left: 4px solid #a8a29e;
}

/* adapt:context — "In your field" subtopic bridge (amber). */
.celltag_adapt\:context {
  background: #fff8e6;
  border-left: 4px solid #e0b34a;
}
.celltag_adapt\:context h3 { color: #8a5a00; }

/* adapt:suggestions — "Go deeper with an LLM" prompts (violet, with Copy button). */
.celltag_adapt\:suggestions {
  background: #f5f0ff;
  border-left: 4px solid #8b5cf6;
}
.celltag_adapt\:suggestions h3 { color: #5b3aa6; }
.celltag_adapt\:suggestions p strong { color: #4c1d95; }
.celltag_adapt\:suggestions pre {
  position: relative;
  background: #ffffff !important;
  border: 1px solid #ddd2f7;
  border-radius: 6px;
  padding: 0.85rem 1rem;
  padding-right: 4.5rem;
  margin: 0.5rem 0 1rem 0;
  white-space: pre-wrap;
  word-break: break-word;
  color: #2d1b69;
  box-shadow: 0 1px 2px rgba(91, 58, 166, 0.06);
}
.celltag_adapt\:suggestions pre code {
  background: transparent !important;
  padding: 0;
  color: inherit;
  font-size: 0.92em;
  line-height: 1.5;
}
.copy-prompt-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: #8b5cf6;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 0.25rem 0.6rem;
  font-size: 0.78rem;
  font-weight: 500;
  cursor: pointer;
  opacity: 0.85;
  transition: opacity 0.15s, background 0.15s;
}
.copy-prompt-btn:hover { opacity: 1; background: #7c3aed; }
.copy-prompt-btn.copied { background: #10b981; }
"""

# Adds a "Copy" button to each <pre> inside an adapt:suggestions cell.
COPY_JS = r"""
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.celltag_adapt\\:suggestions pre').forEach(function (pre) {
    var btn = document.createElement('button');
    btn.className = 'copy-prompt-btn';
    btn.type = 'button';
    btn.textContent = 'Copy';
    btn.addEventListener('click', function () {
      var text = pre.querySelector('code') ? pre.querySelector('code').innerText : pre.innerText;
      navigator.clipboard.writeText(text).then(function () {
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        setTimeout(function () {
          btn.textContent = 'Copy';
          btn.classList.remove('copied');
        }, 1500);
      });
    });
    pre.appendChild(btn);
  });
});
"""


def render_one(nb_path: Path, out_path: Path) -> None:
    nb = nbformat.read(nb_path, as_version=4)
    exporter = HTMLExporter()
    exporter.template_name = "lab"
    body, _resources = exporter.from_notebook_node(nb)
    injection = f"<style>{CONTEXT_CSS}</style><script>{COPY_JS}</script></head>"
    body = body.replace("</head>", injection, 1)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(body, encoding="utf-8")
    print(f"rendered {out_path.relative_to(ROOT)}")


def build_index(persona_links: dict[str, list[tuple[str, str]]]) -> None:
    parts = [
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'>",
        "<title>Background-Adaptive ML Notebooks</title>",
        f"<style>{INDEX_CSS}</style></head><body>",
        "<h1>Background-Adaptive ML Notebooks</h1>",
        "<p class='tag'>One ML tutorial. Re-explained for your field, without losing the fundamentals.</p>",
        "<section><div class='howto'>",
        "<p>Two short Jupyter notebooks teach <strong>linear regression</strong> "
        "and a <strong>tiny neural network</strong>. A VS Code Copilot Chat <em>skill</em> reads a learner's "
        "background and rewrites only the explanation cells &mdash; analogies, examples, "
        "exercises, and copy-pasteable &ldquo;go deeper with an LLM&rdquo; prompts &mdash; "
        "while a glossary-lock keeps every canonical ML term identical across versions.</p>",
        "<p>Below are five pre-rendered adaptations. Pick the one closest to your background, "
        "or clone the repo and run the skill on your own <code>background.md</code>.</p>",
        "</div></section>",
        "<section><h2>Example adaptations</h2><div class='grid'>",
    ]
    for persona, links in persona_links.items():
        title = PERSONA_TITLES.get(persona, persona)
        parts.append(f"<div class='card'><h3>{title}</h3>")
        for label, href in links:
            parts.append(f"<a href='{href}'>{label}</a>")
        parts.append("</div>")
    parts.append("</div></section>")
    parts.append(
        "<section><h2>Try it yourself</h2><div class='howto'>"
        "<p>Clone the repo, open it in VS Code, then in Copilot Chat invoke the "
        "<code>/adapt-notebook</code> skill with a one-line description of yourself "
        "&mdash; the skill will interview you, write your <code>background.md</code>, "
        "and adapt both notebooks to your field. The more detail you give about your "
        "<strong>role, day-to-day work, and what you want to learn</strong>, the better "
        "the analogies and examples will land.</p>"
        "<p><strong>Example &mdash; one-liner that triggers the interview:</strong></p>"
        "<pre style='background:#f5f0ff;border:1px solid #ddd2f7;border-left:4px solid #8b5cf6;"
        "border-radius:6px;padding:0.85rem 1rem;color:#2d1b69;white-space:pre-wrap;'>"
        "/adapt-notebook I'm a marine biologist"
        "</pre>"
        "<p><strong>Example &mdash; richer one-shot description (skips most of the interview):</strong></p>"
        "<pre style='background:#f5f0ff;border:1px solid #ddd2f7;border-left:4px solid #8b5cf6;"
        "border-radius:6px;padding:0.85rem 1rem;color:#2d1b69;white-space:pre-wrap;'>"
        "/adapt-notebook I'm a postdoc marine biologist studying coral reef recovery.\n"
        "I spend most of my week running underwater transects, fitting growth\n"
        "curves to bleaching-recovery data in R, and writing grant reports.\n"
        "I'm comfortable with stats and basic Python. Analogies that would land:\n"
        "reef-fish abundance counts, dose-response to temperature stress,\n"
        "logistic growth of coral cover. Goal: be able to fit my own ML models\n"
        "to next season's transect data."
        "</pre>"
        "<p><strong>Example &mdash; reuse a saved background:</strong></p>"
        "<pre style='background:#f5f0ff;border:1px solid #ddd2f7;border-left:4px solid #8b5cf6;"
        "border-radius:6px;padding:0.85rem 1rem;color:#2d1b69;white-space:pre-wrap;'>"
        "/adapt-notebook use examples/marine_biologist/background.md"
        "</pre>"
        "<p><a href='https://github.com/RT-Rakesh/background-adaptive-ml'>GitHub repository &rarr;</a></p>"
        "</div></section>"
    )
    parts.append("<footer>iamdatascientist.com</footer>")
    parts.append("</body></html>")
    (SITE / "index.html").write_text("\n".join(parts), encoding="utf-8")
    print("rendered site/index.html")


def main() -> None:
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)

    persona_links: dict[str, list[tuple[str, str]]] = {}
    if not EXAMPLES.exists():
        print("no examples/ directory yet — skipping")
        build_index(persona_links)
        return

    for persona_dir in sorted(EXAMPLES.iterdir()):
        if not persona_dir.is_dir():
            continue
        links = []
        for nb in sorted(persona_dir.glob("*.ipynb")):
            out = SITE / persona_dir.name / f"{nb.stem}.html"
            render_one(nb, out)
            label = nb.stem.replace("_", " ").title()
            links.append((label, f"{persona_dir.name}/{nb.stem}.html"))
        if links:
            persona_links[persona_dir.name] = links

    build_index(persona_links)


if __name__ == "__main__":
    main()
