"""Build, validate, and render every persona example.

Run after editing any persona override or any base notebook:
    python scripts/build_all.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
NOTEBOOKS = ROOT / "notebooks"


def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=ROOT)


def main() -> None:
    bases = {
        "01_simple_regression.yaml": NOTEBOOKS / "01_simple_regression.ipynb",
        "02_deep_learning_regression.yaml": NOTEBOOKS / "02_deep_learning_regression.ipynb",
    }
    personas = sorted(p for p in EXAMPLES.iterdir() if p.is_dir())

    failures: list[str] = []
    for persona in personas:
        for spec_name, base in bases.items():
            spec = persona / spec_name
            if not spec.exists():
                continue
            out = persona / spec_name.replace(".yaml", ".ipynb")
            try:
                run([sys.executable, "scripts/apply_persona.py",
                     str(base), str(spec), str(out)])
                run([sys.executable, "scripts/validate_adapted.py",
                     str(base), str(out)])
            except subprocess.CalledProcessError as exc:
                failures.append(f"{persona.name}/{spec_name}: {exc}")

    if failures:
        print("\n=== FAILURES ===")
        for f in failures:
            print(" -", f)
        sys.exit(1)

    run([sys.executable, "scripts/render_showcase.py"])
    print("\nAll personas built, validated, and rendered.")


if __name__ == "__main__":
    main()
